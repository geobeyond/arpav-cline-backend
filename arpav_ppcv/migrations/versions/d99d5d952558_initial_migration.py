"""initial-migration

Revision ID: d99d5d952558
Revises: 
Create Date: 2024-04-10 18:20:55.951581

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel
from geoalchemy2 import Geometry

# revision identifiers, used by Alembic.
revision: str = 'd99d5d952558'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_geospatial_table('station',
    sa.Column('id', sqlmodel.sql.sqltypes.GUID(), nullable=False),
    sa.Column('geom', Geometry(geometry_type='POLYGON', srid=4326, spatial_index=False, from_text='ST_GeomFromEWKT', name='geometry'), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_geospatial_index('idx_station_geom', 'station', ['geom'], unique=False, postgresql_using='gist', postgresql_ops={})
    op.create_table('variable',
    sa.Column('id', sqlmodel.sql.sqltypes.GUID(), nullable=False),
    sa.Column('name', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('unit', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('monthlymeasurement',
    sa.Column('id', sqlmodel.sql.sqltypes.GUID(), nullable=False),
    sa.Column('station_id', sqlmodel.sql.sqltypes.GUID(), nullable=False),
    sa.Column('variable_id', sqlmodel.sql.sqltypes.GUID(), nullable=False),
    sa.ForeignKeyConstraint(['station_id'], ['station.id'], ),
    sa.ForeignKeyConstraint(['variable_id'], ['variable.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('monthlymeasurement')
    op.drop_table('variable')
    op.drop_geospatial_index('idx_station_geom', table_name='station', postgresql_using='gist', column_name='geom')
    op.drop_geospatial_table('station')
    # ### end Alembic commands ###
