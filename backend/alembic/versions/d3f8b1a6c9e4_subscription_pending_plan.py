"""subscriptions: pending_plan/pending_period para el checkout de Flow

Revision ID: d3f8b1a6c9e4
Revises: c1e7a4d9f0b2
Create Date: 2026-07-22

Guardan el plan/periodo elegidos durante el registro de tarjeta (paso checkout),
para crear la suscripcion correcta en /billing/return sin confiar en la URL.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'd3f8b1a6c9e4'
down_revision: Union[str, None] = 'c1e7a4d9f0b2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('subscriptions', sa.Column('pending_plan', sa.String(length=20), nullable=True))
    op.add_column('subscriptions', sa.Column('pending_period', sa.String(length=20), nullable=True))


def downgrade() -> None:
    op.drop_column('subscriptions', 'pending_period')
    op.drop_column('subscriptions', 'pending_plan')
