"""added correspondence between climatic indicator and station manager

Revision ID: f00bbaa17ce6
Revises: 8df4e65677d9
Create Date: 2024-12-16 16:37:27.376823

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'f00bbaa17ce6'
down_revision: Union[str, None] = '8df4e65677d9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    sa.Enum('ARPAV', 'ARPAFVG', name='observationstationmanager').create(op.get_bind())
    op.create_table('climaticindicatorobservationname',
    sa.Column('climatic_indicator_id', sa.Integer(), nullable=False),
    sa.Column('station_manager', postgresql.ENUM('ARPAV', 'ARPAFVG', name='observationstationmanager', create_type=False), nullable=False),
    sa.Column('indicator_observation_name', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.ForeignKeyConstraint(['climatic_indicator_id'], ['climaticindicator.id'], onupdate='CASCADE', ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('climatic_indicator_id', 'station_manager')
    )
    op.add_column('observationstation', sa.Column('managed_by', postgresql.ENUM('ARPAV', 'ARPAFVG', name='observationstationmanager', create_type=False), nullable=False))
    op.drop_column('observationstation', 'owner')
    sa.Enum('ARPAV', 'ARPAFVG', name='observationstationowner').drop(op.get_bind())
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    sa.Enum('ARPAV', 'ARPAFVG', name='observationstationowner').create(op.get_bind())
    op.add_column('observationstation', sa.Column('owner', postgresql.ENUM('ARPAV', 'ARPAFVG', name='observationstationowner', create_type=False), autoincrement=False, nullable=False))
    op.drop_column('observationstation', 'managed_by')
    op.drop_table('climaticindicatorobservationname')
    sa.Enum('ARPAV', 'ARPAFVG', name='observationstationmanager').drop(op.get_bind())
    # ### end Alembic commands ###
