from ...schemas.coverages import HistoricalCoverageConfigurationCreate
from ...schemas.static import (
    HistoricalDecade,
    HistoricalReferencePeriod,
)


def generate_historical_coverage_configurations(
    climatic_indicator_ids: dict[str, int],
    spatial_region_ids: dict[str, int],
    year_period_groups: dict[str, int],
    observation_series_configuration_ids: dict[str, int],
) -> list[HistoricalCoverageConfigurationCreate]:
    return [
        HistoricalCoverageConfigurationCreate(
            climatic_indicator_id=climatic_indicator_ids["hdds-absolute-annual"],
            spatial_region_id=spatial_region_ids["arpa_v"],
            netcdf_main_dataset_name="{climatic_indicator}",
            year_period_group=year_period_groups["only_year"],
            thredds_url_pattern="cline_yr/{climatic_indicator}_{year_period}_????-????_py85.nc",
            wms_main_layer_name="{climatic_indicator}",
            observation_series_configurations=[
                observation_series_configuration_ids[
                    "hdds-absolute-annual-arpa_v-yearly"
                ],
            ],
        ),
        HistoricalCoverageConfigurationCreate(
            climatic_indicator_id=climatic_indicator_ids["hdds-anomaly-annual"],
            spatial_region_id=spatial_region_ids["arpa_v"],
            netcdf_main_dataset_name="{climatic_indicator}_diff",
            reference_period=HistoricalReferencePeriod.CLIMATE_STANDARD_NORMAL_1991_2020,
            year_period_group=year_period_groups["only_year"],
            thredds_url_pattern="cline_yr/anomalia1yr/{climatic_indicator}_{year_period}_????-????_diff_{reference_period}.nc",
            wms_main_layer_name="{climatic_indicator}_diff",
            observation_series_configurations=[
                observation_series_configuration_ids[
                    "hdds-absolute-annual-arpa_v-yearly"
                ],
            ],
        ),
        HistoricalCoverageConfigurationCreate(
            climatic_indicator_id=climatic_indicator_ids["hdds-absolute-ten_year"],
            spatial_region_id=spatial_region_ids["arpa_v"],
            netcdf_main_dataset_name="{year_period}_avg",
            decades=[
                HistoricalDecade.DECADE_1991_2000,
                HistoricalDecade.DECADE_2001_2010,
                HistoricalDecade.DECADE_2011_2020,
            ],
            reference_period=HistoricalReferencePeriod.CLIMATE_STANDARD_NORMAL_1991_2020,
            year_period_group=year_period_groups["only_year"],
            thredds_url_pattern="cline_10yr/{climatic_indicator}_{decade}_ref{reference_period}.nc",
            wms_main_layer_name="{year_period}_avg",
            observation_series_configurations=[
                observation_series_configuration_ids[
                    "hdds-absolute-annual-arpa_v-yearly"
                ],
            ],
        ),
        HistoricalCoverageConfigurationCreate(
            climatic_indicator_id=climatic_indicator_ids["hdds-anomaly-ten_year"],
            spatial_region_id=spatial_region_ids["arpa_v"],
            netcdf_main_dataset_name="{year_period}_diffavg_{reference_period}",
            decades=[
                HistoricalDecade.DECADE_1991_2000,
                HistoricalDecade.DECADE_2001_2010,
                HistoricalDecade.DECADE_2011_2020,
            ],
            reference_period=HistoricalReferencePeriod.CLIMATE_STANDARD_NORMAL_1991_2020,
            year_period_group=year_period_groups["only_year"],
            thredds_url_pattern="cline_10yr/{climatic_indicator}_{decade}_ref{reference_period}.nc",
            wms_main_layer_name="{year_period}_avg",
            observation_series_configurations=[
                observation_series_configuration_ids[
                    "hdds-absolute-annual-arpa_v-yearly"
                ],
            ],
        ),
        HistoricalCoverageConfigurationCreate(
            climatic_indicator_id=climatic_indicator_ids["hdds-absolute-thirty_year"],
            spatial_region_id=spatial_region_ids["arpa_v"],
            netcdf_main_dataset_name="{year_period}_avg",
            reference_period=HistoricalReferencePeriod.CLIMATE_STANDARD_NORMAL_1991_2020,
            year_period_group=year_period_groups["only_year"],
            thredds_url_pattern="cline_30yr/{climatic_indicator}_{reference_period}.nc",
            wms_main_layer_name="{year_period}_avg",
            observation_series_configurations=[
                observation_series_configuration_ids[
                    "hdds-absolute-annual-arpa_v-yearly"
                ],
            ],
        ),
    ]
