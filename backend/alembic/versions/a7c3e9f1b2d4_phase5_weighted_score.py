"""phase 5: motor de score ponderado por industria

Revision ID: a7c3e9f1b2d4
Revises: f1a2b3c4d5e6
Create Date: 2026-06-14

Fase 5 (motor de score defensible):
- organizations.industry: industria de la org, elige el perfil de pesos.
- evaluations.score_weighted: puntaje ponderado por dimensión (Seguridad pesa más
  que Puntualidad en construcción/minería). Backfill con el perfil default, que es
  el que aplica a todas las orgs existentes (todas nacen 'construccion_mineria').
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a7c3e9f1b2d4'
down_revision: Union[str, Sequence[str], None] = 'f1a2b3c4d5e6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Industria de la organización (perfil de pesos del puntaje).
    op.add_column(
        'organizations',
        sa.Column('industry', sa.String(length=50), server_default='construccion_mineria', nullable=False),
    )

    # Puntaje ponderado por evaluación. Se agrega nullable para poder backfillear
    # las filas existentes y luego se fija NOT NULL.
    op.add_column('evaluations', sa.Column('score_weighted', sa.Float(), nullable=True))

    # Backfill con el perfil 'construccion_mineria' (default de toda org existente):
    # quality .25 + safety .30 + punctuality .10 + teamwork .15 + technical .20
    op.execute(
        """
        UPDATE evaluations SET score_weighted = ROUND(
            (score_quality * 0.25
             + score_safety * 0.30
             + score_punctuality * 0.10
             + score_teamwork * 0.15
             + score_technical * 0.20)::numeric, 2
        )
        """
    )

    op.alter_column('evaluations', 'score_weighted', nullable=False, server_default='0')
    op.create_index('ix_evaluations_score_weighted', 'evaluations', ['score_weighted'], unique=False)


def downgrade() -> None:
    op.drop_index('ix_evaluations_score_weighted', table_name='evaluations')
    op.drop_column('evaluations', 'score_weighted')
    op.drop_column('organizations', 'industry')
