import sqlmodel

from ... import database
from . import schemas


def get_forecast_advanced_section_navigation(
    session: sqlmodel.Session
) -> list[schemas.ForecastCoverageNavigationSection]:
    sections = {}
    for forecast_cov_conf in database.collect_all_forecast_coverage_configurations(session):
        indicator_section = sections.setdefault(
            forecast_cov_conf.identifier,
            schemas.ForecastCoverageNavigationSection(
                climatic_indicator=forecast_cov_conf.climatic_indicator,
            )
        )
        included_model_ids = [fm.id for fm in indicator_section.forecast_models]
        indicator_section.forecast_models.extend(
            fml.forecast_model for fml in forecast_cov_conf.forecast_model_links
            if fml.forecast_model_id not in included_model_ids
        )
        indicator_section.scenarios.extend(
            s for s in forecast_cov_conf.scenarios
            if s not in indicator_section.scenarios)
        indicator_section.year_periods.extend(
            yp for yp in forecast_cov_conf.year_periods
            if yp not in indicator_section.year_periods
        )
        included_time_window_ids = [tw.id for tw in indicator_section.time_windows]
        indicator_section.time_windows.extend(
            twl.forecast_time_window for twl in forecast_cov_conf.forecast_time_window_links
            if twl.forecast_time_window_id not in included_time_window_ids
        )
    return list(sections.values())
