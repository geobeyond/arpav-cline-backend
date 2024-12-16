"""rename station owners to managers

Revision ID: 41c6050a217c
Revises: f00bbaa17ce6
Create Date: 2024-12-16 18:19:22.357221

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '41c6050a217c'
down_revision: Union[str, None] = 'f00bbaa17ce6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('observationseriesconfiguration', sa.Column('station_managers', sa.ARRAY(sa.String()), nullable=True))
    op.drop_column('observationseriesconfiguration', 'station_owners')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('observationseriesconfiguration', sa.Column('station_owners', postgresql.ARRAY(sa.VARCHAR()), autoincrement=False, nullable=True))
    op.drop_column('observationseriesconfiguration', 'station_managers')
    # ### end Alembic commands ###
