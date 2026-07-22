"""contract_acceptances: registro de aceptacion del contrato por usuario

Revision ID: c1e7a4d9f0b2
Revises: 019426b0cd06
Create Date: 2026-07-22

Prueba legal de la aceptacion del Contrato/Terminos (Ley 19.799): una fila por
(usuario, version) con IP y user-agent. Solo se agrega, nunca se modifica ni borra.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = 'c1e7a4d9f0b2'
down_revision: Union[str, None] = '019426b0cd06'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'contract_acceptances',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('contract_version', sa.String(length=20), nullable=False),
        sa.Column('accepted_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('ip', sa.String(length=64), nullable=True),
        sa.Column('user_agent', sa.String(length=400), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_contract_acceptances_user_id', 'contract_acceptances', ['user_id'])
    op.create_index(
        'ix_contract_acceptances_user_version', 'contract_acceptances',
        ['user_id', 'contract_version'], unique=True,
    )


def downgrade() -> None:
    op.drop_index('ix_contract_acceptances_user_version', table_name='contract_acceptances')
    op.drop_index('ix_contract_acceptances_user_id', table_name='contract_acceptances')
    op.drop_table('contract_acceptances')
