"""netcdf var name for uncertainties

Revision ID: a39792a72d70
Revises: a410aa66a691
Create Date: 2025-01-29 16:51:12.778688

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = 'a39792a72d70'
down_revision: Union[str, None] = 'a410aa66a691'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('forecastcoverageconfiguration', sa.Column('lower_uncertainty_netcdf_main_dataset_name', sqlmodel.sql.sqltypes.AutoString(), nullable=True))
    op.add_column('forecastcoverageconfiguration', sa.Column('upper_uncertainty_netcdf_main_dataset_name', sqlmodel.sql.sqltypes.AutoString(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('forecastcoverageconfiguration', 'upper_uncertainty_netcdf_main_dataset_name')
    op.drop_column('forecastcoverageconfiguration', 'lower_uncertainty_netcdf_main_dataset_name')
    # ### end Alembic commands ###
