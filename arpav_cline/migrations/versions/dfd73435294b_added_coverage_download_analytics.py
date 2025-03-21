"""added coverage download analytics

Revision ID: dfd73435294b
Revises: 2f2c1575c72b
Create Date: 2025-03-04 13:50:05.380878

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = 'dfd73435294b'
down_revision: Union[str, None] = '2f2c1575c72b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('forecastcoveragedownloadrequest',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('request_datetime', sa.DateTime(), nullable=False),
    sa.Column('entity_name', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
    sa.Column('is_public_sector', sa.Boolean(), nullable=False),
    sa.Column('download_reason', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('climatological_variable', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('aggregation_period', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('measure_type', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('year_period', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('climatological_model', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('scenario', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('time_window', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('historicalcoveragedownloadrequest',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('request_datetime', sa.DateTime(), nullable=False),
    sa.Column('entity_name', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
    sa.Column('is_public_sector', sa.Boolean(), nullable=False),
    sa.Column('download_reason', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('climatological_variable', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('aggregation_period', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('measure_type', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('year_period', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('decade', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
    sa.Column('reference_period', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('historicalcoveragedownloadrequest')
    op.drop_table('forecastcoveragedownloadrequest')
    # ### end Alembic commands ###
