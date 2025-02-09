"""added historical_cov_confs

Revision ID: 2ddb8e06710c
Revises: 7067c8da7c49
Create Date: 2025-02-09 00:40:22.809496

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel
from alembic_postgresql_enum import TableReference
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '2ddb8e06710c'
down_revision: Union[str, None] = '7067c8da7c49'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    sa.Enum(
        'ALL_YEAR', 'WINTER', 'SPRING', 'SUMMER', 'AUTUMN', 'JANUARY',
        'FEBRUARY', 'MARCH', 'APRIL', 'MAY', 'JUNE', 'JULY', 'AUGUST',
        'SEPTEMBER', 'OCTOBER', 'NOVEMBER', 'DECEMBER',
        name='historicalyearperiod'
    ).create(op.get_bind())
    sa.Enum(
        'DECADE_1961_1970', 'DECADE_1971_1980', 'DECADE_1981_1990',
        'DECADE_1991_2000', 'DECADE_2001_2010', 'DECADE_2011_2020',
        'DECADE_2021_2030', 'DECADE_2031_2040',
        name='historicaldecade'
    ).create(op.get_bind())
    sa.Enum(
        'CLIMATE_STANDARD_NORMAL_1961_1990',
        'CLIMATE_STANDARD_NORMAL_1991_2020',
        name='historicalreferenceperiod'
    ).create(op.get_bind())
    op.add_column('climaticindicator', sa.Column('historical_coverages_internal_name', sqlmodel.sql.sqltypes.AutoString(), nullable=True))
    op.add_column('historicalcoverageconfiguration', sa.Column('reference_period', postgresql.ENUM('CLIMATE_STANDARD_NORMAL_1961_1990', 'CLIMATE_STANDARD_NORMAL_1991_2020', name='historicalreferenceperiod', create_type=False), nullable=True))
    op.add_column('historicalcoverageconfiguration', sa.Column('wms_main_layer_name', sqlmodel.sql.sqltypes.AutoString(), nullable=False))
    op.add_column('historicalcoverageconfiguration', sa.Column('decades', sa.ARRAY(postgresql.ENUM('DECADE_1961_1970', 'DECADE_1971_1980', 'DECADE_1981_1990', 'DECADE_1991_2000', 'DECADE_2001_2010', 'DECADE_2011_2020', 'DECADE_2021_2030', 'DECADE_2031_2040', name='historicaldecade', create_type=False)), nullable=True))
    op.alter_column(
        'historicalcoverageconfiguration',
        'year_periods',
        existing_type=postgresql.ARRAY(sa.VARCHAR()),
        postgresql_using='year_periods::historicalyearperiod[]',
        type_=sa.ARRAY(
            sa.Enum(
                'ALL_YEAR', 'WINTER', 'SPRING', 'SUMMER', 'AUTUMN', 'JANUARY',
                'FEBRUARY', 'MARCH', 'APRIL', 'MAY', 'JUNE', 'JULY', 'AUGUST',
                'SEPTEMBER', 'OCTOBER', 'NOVEMBER', 'DECEMBER',
                name='historicalyearperiod'
            )
        ),
        existing_nullable=True
    )
    op.sync_enum_values(
        enum_schema='public',
        enum_name='aggregationperiod',
        new_values=['ANNUAL', 'TEN_YEAR', 'THIRTY_YEAR'],
        affected_columns=[TableReference(table_schema='public', table_name='climaticindicator', column_name='aggregation_period')],
        enum_values_to_rename=[],
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.sync_enum_values(
        enum_schema='public',
        enum_name='aggregationperiod',
        new_values=['ANNUAL', 'THIRTY_YEAR'],
        affected_columns=[TableReference(table_schema='public', table_name='climaticindicator', column_name='aggregation_period')],
        enum_values_to_rename=[],
    )
    op.alter_column('historicalcoverageconfiguration', 'year_periods',
               existing_type=sa.ARRAY(sa.Enum('ALL_YEAR', 'WINTER', 'SPRING', 'SUMMER', 'AUTUMN', 'JANUARY', 'FEBRUARY', 'MARCH', 'APRIL', 'MAY', 'JUNE', 'JULY', 'AUGUST', 'SEPTEMBER', 'OCTOBER', 'NOVEMBER', 'DECEMBER', name='historicalyearperiod')),
               type_=postgresql.ARRAY(sa.VARCHAR()),
               existing_nullable=True)
    op.drop_column('historicalcoverageconfiguration', 'decades')
    op.drop_column('historicalcoverageconfiguration', 'wms_main_layer_name')
    op.drop_column('historicalcoverageconfiguration', 'reference_period')
    op.drop_column('climaticindicator', 'historical_coverages_internal_name')
    sa.Enum('CLIMATE_STANDARD_NORMAL_1961_1990', 'CLIMATE_STANDARD_NORMAL_1991_2020', name='historicalreferenceperiod').drop(op.get_bind())
    sa.Enum('DECADE_1961_1970', 'DECADE_1971_1980', 'DECADE_1981_1990', 'DECADE_1991_2000', 'DECADE_2001_2010', 'DECADE_2011_2020', 'DECADE_2021_2030', 'DECADE_2031_2040', name='historicaldecade').drop(op.get_bind())
    sa.Enum('ALL_YEAR', 'WINTER', 'SPRING', 'SUMMER', 'AUTUMN', 'JANUARY', 'FEBRUARY', 'MARCH', 'APRIL', 'MAY', 'JUNE', 'JULY', 'AUGUST', 'SEPTEMBER', 'OCTOBER', 'NOVEMBER', 'DECEMBER', name='historicalyearperiod').drop(op.get_bind())
    # ### end Alembic commands ###
