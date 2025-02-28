import logging
from typing import (
    Optional,
    TYPE_CHECKING,
)
import dataclasses

import cftime
import netCDF4
import pandas as pd

if TYPE_CHECKING:
    from ..config import ThreddsServerSettings
    from ..schemas.overviews import (
        ForecastOverviewSeriesInternal,
        ObservationOverviewSeriesInternal,
    )


logger = logging.getLogger(__name__)


@dataclasses.dataclass
class ObservationOverviewDataRetriever:
    settings: "ThreddsServerSettings"
    overview_series: "ObservationOverviewSeriesInternal"

    def retrieve_main_data(
        self,
        target_series_name: str,
    ) -> Optional[pd.Series]:
        opendap_url = self.overview_series.get_thredds_opendap_url(self.settings)
        netcdf_variable_name = self.overview_series.get_netcdf_main_dataset_name()
        result = None
        if all((opendap_url, netcdf_variable_name)):
            result = _retrieve_data(
                opendap_url, netcdf_variable_name, target_series_name
            )
        elif opendap_url is None:
            logger.warning("Could not find overview series' OpenDAP URL")
        else:
            logger.warning("Could not find overview series' NetCDF variable name")
        return result


@dataclasses.dataclass
class ForecastOverviewDataRetriever:
    settings: "ThreddsServerSettings"
    overview_series: "ForecastOverviewSeriesInternal"

    def retrieve_main_data(
        self,
        target_series_name: str,
    ) -> Optional[pd.Series]:
        opendap_url = self.overview_series.get_thredds_opendap_url(self.settings)
        netcdf_variable_name = self.overview_series.get_netcdf_main_dataset_name()
        result = None
        if all((opendap_url, netcdf_variable_name)):
            result = _retrieve_data(
                opendap_url, netcdf_variable_name, target_series_name
            )
        elif opendap_url is None:
            logger.warning("Could not find overview series' OpenDAP URL")
        else:
            logger.warning("Could not find overview series' NetCDF variable name")
        return result

    def retrieve_lower_uncertainty_data(
        self,
        target_series_name: str,
    ) -> Optional[pd.Series]:
        opendap_url = self.overview_series.get_lower_uncertainty_thredds_opendap_url(
            self.settings
        )
        netcdf_variable_name = (
            self.overview_series.get_netcdf_lower_uncertainty_main_dataset_name()
        )
        result = None
        if all((opendap_url, netcdf_variable_name)):
            result = _retrieve_data(
                opendap_url,
                netcdf_variable_name,
                target_series_name,
            )
        elif opendap_url is None:
            logger.warning(
                "Could not find overview series' lower uncertainty OpenDAP URL"
            )
        else:
            logger.warning(
                "Could not find overview series' lower uncertainty NetCDF variable name"
            )
        return result

    def retrieve_upper_uncertainty_data(
        self,
        target_series_name: str,
    ) -> Optional[pd.Series]:
        opendap_url = self.overview_series.get_upper_uncertainty_thredds_opendap_url(
            self.settings
        )
        netcdf_variable_name = (
            self.overview_series.get_netcdf_upper_uncertainty_main_dataset_name()
        )
        result = None
        if all((opendap_url, netcdf_variable_name)):
            result = _retrieve_data(
                opendap_url,
                netcdf_variable_name,
                target_series_name,
            )
        elif opendap_url is None:
            logger.warning(
                "Could not find overview series' upper uncertainty OpenDAP URL"
            )
        else:
            logger.warning(
                "Could not find overview series' upper uncertainty NetCDF variable name"
            )
        return result


def _retrieve_data(
    opendap_url: str,
    netcdf_variable_name: str,
    target_series_name: str,
) -> pd.Series:
    ds = netCDF4.Dataset(opendap_url)
    df = pd.DataFrame(
        {
            "time": pd.Series(
                cftime.num2pydate(
                    ds.variables["time"][:],
                    units=ds.variables["time"].units,
                    calendar=ds.variables["time"].calendar,
                )
            ),
            target_series_name: pd.Series(
                ds.variables[netcdf_variable_name][:].ravel(),
            ),
        }
    )
    ds.close()
    df.set_index("time", inplace=True)
    return df.squeeze()
