"""made forecast model name unique

Revision ID: 132a6f461620
Revises: 5dec4a8e29cb
Create Date: 2025-01-17 15:48:18.810836

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = '132a6f461620'
down_revision: Union[str, None] = '5dec4a8e29cb'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_unique_constraint(None, 'forecastmodel', ['name'])
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'forecastmodel', type_='unique')
    # ### end Alembic commands ###
