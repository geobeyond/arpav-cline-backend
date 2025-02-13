"""added link between historical covs and observation series confs

Revision ID: 2551ade57d32
Revises: 2ddb8e06710c
Create Date: 2025-02-13 18:47:54.146771

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = '2551ade57d32'
down_revision: Union[str, None] = '2ddb8e06710c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('historicalcoverageconfigurationobservationseriesconfigurationlink',
    sa.Column('historical_coverage_configuration_id', sa.Integer(), nullable=False),
    sa.Column('observation_series_configuration_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['historical_coverage_configuration_id'], ['historicalcoverageconfiguration.id'], onupdate='CASCADE', ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['observation_series_configuration_id'], ['observationseriesconfiguration.id'], onupdate='CASCADE', ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('historical_coverage_configuration_id', 'observation_series_configuration_id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('historicalcoverageconfigurationobservationseriesconfigurationlink')
    # ### end Alembic commands ###
