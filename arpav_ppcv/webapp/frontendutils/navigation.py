import sqlmodel

from ...db import collect_all_forecast_coverage_configurations
from . import schemas


def get_forecast_advanced_section_navigation(
    session: sqlmodel.Session,
) -> list[schemas.ForecastCoverageNavigationSection]:
    sections = {}
    for forecast_cov_conf in collect_all_forecast_coverage_configurations(
        session
    ):
        indicator_section = sections.setdefault(
            forecast_cov_conf.climatic_indicator.identifier,
            schemas.ForecastCoverageNavigationSection(
                climatic_indicator=forecast_cov_conf.climatic_indicator,
            ),
        )
        included_model_ids = [fm.id for fm in indicator_section.forecast_models]
        indicator_section.forecast_models.extend(
            fml.forecast_model
            for fml in forecast_cov_conf.forecast_model_links
            if fml.forecast_model_id not in included_model_ids
        )
        indicator_section.scenarios.extend(
            s
            for s in forecast_cov_conf.scenarios
            if s not in indicator_section.scenarios
        )
        indicator_section.year_periods.extend(
            yp
            for yp in forecast_cov_conf.year_periods
            if yp not in indicator_section.year_periods
        )
        included_time_window_ids = [tw.id for tw in indicator_section.time_windows]
        indicator_section.time_windows.extend(
            twl.forecast_time_window
            for twl in forecast_cov_conf.forecast_time_window_links
            if twl.forecast_time_window_id not in included_time_window_ids
        )
    # now sort stuff according to the predefined order
    result = sorted(
        list(sections.values()),
        key=lambda section: (
            section.climatic_indicator.sort_order,
            section.climatic_indicator.measure_type.get_sort_order(),
        ),
    )
    for nav_section in result:
        nav_section: schemas.ForecastCoverageNavigationSection
        nav_section.forecast_models.sort(key=lambda fm: fm.sort_order)
        nav_section.scenarios.sort(key=lambda s: s.get_sort_order())
        nav_section.year_periods.sort(key=lambda yp: yp.get_sort_order())
        nav_section.time_windows.sort(key=lambda tw: tw.sort_order)
    return result
