"""added precision to cov conf

Revision ID: 4df282a0319d
Revises: c6f618a7f88f
Create Date: 2024-10-16 13:39:58.363787

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
_table_name = "coverageconfiguration"
_column_name = "data_precision"

class CoverageConfiguration(Base):
    __tablename__ = _table_name

    id = sa.Column(sa.UUID, primary_key=True)
    data_precision = sa.Column(sa.Integer, nullable=True)


# revision identifiers, used by Alembic.
revision: str = "4df282a0319d"
down_revision: Union[str, None] = "c6f618a7f88f"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    op.add_column(
        _table_name,
        sa.Column(_column_name, sa.Integer(), nullable=True)
    )
    session = sa.orm.Session(bind=bind)
    for cov_conf in session.query(CoverageConfiguration):
        cov_conf.data_precision = 3
    session.commit()
    op.alter_column(_table_name, _column_name, nullable=False)


def downgrade() -> None:
    op.drop_column('coverageconfiguration', 'data_precision')
