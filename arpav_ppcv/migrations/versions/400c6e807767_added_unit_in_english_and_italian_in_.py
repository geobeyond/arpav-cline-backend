"""added unit in english and italian in cov conf

Revision ID: 400c6e807767
Revises: 002385d70ff0
Create Date: 2024-09-16 17:12:33.781206

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = '400c6e807767'
down_revision: Union[str, None] = '002385d70ff0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column('coverageconfiguration', 'unit', new_column_name='unit_english')
    op.add_column('coverageconfiguration', sa.Column('unit_italian', sqlmodel.sql.sqltypes.AutoString(), nullable=True))


def downgrade() -> None:
    op.alter_column('coverageconfiguration', 'unit_english', new_column_name='unit')
    op.drop_column('coverageconfiguration', 'unit_italian')
