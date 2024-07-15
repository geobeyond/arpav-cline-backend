"""rename conf param description

Revision ID: 0614edfff467
Revises: f6b6c5d996a6
Create Date: 2024-07-01 10:38:57.902311

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = '0614edfff467'
down_revision: Union[str, None] = 'f6b6c5d996a6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('configurationparameter', sa.Column('description_english', sqlmodel.sql.sqltypes.AutoString(), nullable=True))
    op.drop_column('configurationparameter', 'description')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('configurationparameter', sa.Column('description', sa.VARCHAR(), autoincrement=False, nullable=False))
    op.drop_column('configurationparameter', 'description_english')
    # ### end Alembic commands ###
