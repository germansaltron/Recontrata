"""phase 1: soft-delete + audit log + worker consent

Revision ID: f1a2b3c4d5e6
Revises: d4b28c6514bc
Create Date: 2026-06-04

Fase 1 (confianza y riesgo legal):
- evaluations.deleted_at: soft-delete de evaluaciones (L3).
- evaluation_audit_log: rastro/versionado de evaluaciones (L3 + L5).
- worker_consent: consentimiento intra-organización del trabajador (L4).
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = 'f1a2b3c4d5e6'
down_revision: Union[str, Sequence[str], None] = 'd4b28c6514bc'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # L3: soft-delete de evaluaciones
    op.add_column('evaluations', sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True))

    # La unicidad (project_id, worker_id) debe aplicar solo a evaluaciones ACTIVAS,
    # para poder re-evaluar tras un soft-delete. Se reemplaza la constraint por un
    # índice único parcial.
    op.drop_constraint('uq_evaluation_project_worker', 'evaluations', type_='unique')
    op.create_index(
        'uq_evaluation_project_worker_active', 'evaluations', ['project_id', 'worker_id'],
        unique=True, postgresql_where=sa.text('deleted_at IS NULL'),
    )

    # L3 + L5: rastro de auditoría / versionado
    op.create_table(
        'evaluation_audit_log',
        sa.Column('id', sa.UUID(), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('evaluation_id', sa.UUID(), nullable=True),
        sa.Column('org_id', sa.UUID(), nullable=False),
        sa.Column('action', sa.String(length=20), nullable=False),
        sa.Column('actor_id', sa.UUID(), nullable=True),
        sa.Column('actor_name', sa.String(length=255), nullable=True),
        sa.Column('snapshot', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('changed_fields', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['evaluation_id'], ['evaluations.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['org_id'], ['organizations.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['actor_id'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_eval_audit_evaluation_id', 'evaluation_audit_log', ['evaluation_id'], unique=False)
    op.create_index('ix_eval_audit_org_id', 'evaluation_audit_log', ['org_id'], unique=False)

    # L4: consentimiento del trabajador
    op.create_table(
        'worker_consent',
        sa.Column('id', sa.UUID(), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('worker_id', sa.UUID(), nullable=False),
        sa.Column('org_id', sa.UUID(), nullable=False),
        sa.Column('status', sa.String(length=20), server_default='pending', nullable=False),
        sa.Column('method', sa.String(length=20), nullable=True),
        sa.Column('consent_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('recorded_by', sa.UUID(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['worker_id'], ['workers.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['org_id'], ['organizations.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['recorded_by'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('worker_id', name='uq_worker_consent_worker'),
    )
    op.create_index('ix_worker_consent_org_id', 'worker_consent', ['org_id'], unique=False)


def downgrade() -> None:
    op.drop_index('uq_evaluation_project_worker_active', table_name='evaluations')
    op.create_unique_constraint('uq_evaluation_project_worker', 'evaluations', ['project_id', 'worker_id'])
    op.drop_index('ix_worker_consent_org_id', table_name='worker_consent')
    op.drop_table('worker_consent')
    op.drop_index('ix_eval_audit_org_id', table_name='evaluation_audit_log')
    op.drop_index('ix_eval_audit_evaluation_id', table_name='evaluation_audit_log')
    op.drop_table('evaluation_audit_log')
    op.drop_column('evaluations', 'deleted_at')
