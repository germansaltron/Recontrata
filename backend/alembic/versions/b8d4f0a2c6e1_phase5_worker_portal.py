"""phase 5: portal del trabajador (token + derecho a replica)

Revision ID: b8d4f0a2c6e1
Revises: a7c3e9f1b2d4
Create Date: 2026-06-14

Fase 5 (apuesta #2 — Portal del Trabajador):
- workers.portal_token: enlace privado e impredecible para que el trabajador vea su
  historial sin login (se genera bajo demanda, unico, revocable).
- evaluations.worker_reply + worker_reply_at: derecho a replica del trabajador,
  permanente y visible para ambas partes.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b8d4f0a2c6e1'
down_revision: Union[str, Sequence[str], None] = 'a7c3e9f1b2d4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('workers', sa.Column('portal_token', sa.String(length=64), nullable=True))
    op.create_unique_constraint('uq_workers_portal_token', 'workers', ['portal_token'])

    op.add_column('evaluations', sa.Column('worker_reply', sa.Text(), nullable=True))
    op.add_column('evaluations', sa.Column('worker_reply_at', sa.DateTime(timezone=True), nullable=True))


def downgrade() -> None:
    op.drop_column('evaluations', 'worker_reply_at')
    op.drop_column('evaluations', 'worker_reply')
    op.drop_constraint('uq_workers_portal_token', 'workers', type_='unique')
    op.drop_column('workers', 'portal_token')
