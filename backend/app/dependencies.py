"""Shared FastAPI dependencies: auth + org-scoped access."""

import uuid

import jwt
import structlog
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import verify_clerk_token
from app.config import settings
from app.database import get_db
from app.errors import ErrorCode
from app.models.organization import OrgMember
from app.models.user import User

logger = structlog.get_logger()

_bearer_scheme = HTTPBearer(auto_error=False)


async def get_current_user(
    db: AsyncSession = Depends(get_db),
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer_scheme),
) -> User:
    if settings.AUTH_MOCK_ENABLED:
        return await _get_or_create_mock_user(db)

    if not credentials:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing authorization header")

    try:
        claims = await verify_clerk_token(credentials.credentials)
    except jwt.PyJWTError as e:
        logger.warning("JWT verification failed", error=str(e))
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")

    clerk_id = claims.get("sub")
    if not clerk_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token missing subject claim")

    result = await db.execute(select(User).where(User.clerk_id == clerk_id))
    user = result.scalar_one_or_none()

    if not user:
        email = claims.get("email", "")
        full_name = claims.get("name", "")
        user = User(clerk_id=clerk_id, email=email, full_name=full_name)
        db.add(user)
        await db.commit()
        await db.refresh(user)
        logger.info("Auto-provisioned user from Clerk", clerk_id=clerk_id, email=email)

    return user


async def _get_or_create_mock_user(db: AsyncSession) -> User:
    dev_clerk_id = "dev_user_001"
    result = await db.execute(select(User).where(User.clerk_id == dev_clerk_id))
    user = result.scalar_one_or_none()

    if not user:
        user = User(clerk_id=dev_clerk_id, email="dev@faenascore.local", full_name="Dev User")
        db.add(user)
        await db.commit()
        await db.refresh(user)

    return user


async def get_org_member(
    org_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> OrgMember:
    """Verify the current user is a member of the specified organization."""
    result = await db.execute(
        select(OrgMember).where(OrgMember.org_id == org_id, OrgMember.user_id == user.id)
    )
    member = result.scalar_one_or_none()

    if not member:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"detail": "Not a member of this organization", "code": ErrorCode.NOT_ORG_MEMBER},
        )

    return member


async def get_org_admin(
    org_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> OrgMember:
    """Verify the current user is an admin of the specified organization."""
    member = await get_org_member(org_id, db, user)

    if member.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"detail": "Admin access required", "code": ErrorCode.NOT_ORG_ADMIN},
        )

    return member
