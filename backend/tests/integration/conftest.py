"""Harness de integración para tests con DB real (Postgres).

Se activa solo si TEST_DATABASE_URL apunta a un Postgres alcanzable; si no, los
tests de integración se SALTAN (los tests unitarios puros siguen corriendo sin DB).

Provee:
- un esquema limpio por test (create_all/drop_all),
- un AsyncClient sobre la app real,
- override de get_db (sesión de test) y get_current_user (actuar como cualquier user).
"""
import os
import uuid
from dataclasses import dataclass

import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

# Importar la app fuerza el registro de todos los modelos en Base.metadata.
from app.main import app
from app.database import get_db
from app.dependencies import get_current_user
from app.models import Base
from app.models.user import User

TEST_DATABASE_URL = os.environ.get("TEST_DATABASE_URL")


@pytest_asyncio.fixture
async def engine():
    if not TEST_DATABASE_URL:
        import pytest
        pytest.skip("TEST_DATABASE_URL no definido; se omiten los tests de integración.")
    eng = create_async_engine(TEST_DATABASE_URL, poolclass=NullPool)
    async with eng.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield eng
    async with eng.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await eng.dispose()


@dataclass
class Harness:
    client: AsyncClient
    session_maker: async_sessionmaker
    _user: User | None = None

    def act_as(self, user: User | None) -> None:
        self._user = user

    async def create_user(self, name: str) -> User:
        async with self.session_maker() as s:
            u = User(clerk_id=f"test_{uuid.uuid4().hex}", email=f"{name}@test.local", full_name=name)
            s.add(u)
            await s.commit()
            await s.refresh(u)
            return u


@pytest_asyncio.fixture
async def hx(engine):
    sm = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    harness = Harness(client=None, session_maker=sm)  # type: ignore[arg-type]

    async def _get_db():
        async with sm() as session:
            yield session

    def _get_user():
        return harness._user

    app.dependency_overrides[get_db] = _get_db
    app.dependency_overrides[get_current_user] = _get_user

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        harness.client = client
        yield harness

    app.dependency_overrides.clear()
