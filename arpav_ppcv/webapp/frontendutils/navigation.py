import sqlmodel
from arpav_ppcv.db import collect_all_historical_coverage_configurations

from ...db import collect_all_forecast_coverage_configurations
from . import schemas


def get_forecast_advanced_section_navigation(
    session: sqlmodel.Session,
) -> list[schemas.ForecastCoverageNavigationSection]:
    sections = {}
    for cov_conf in collect_all_forecast_coverage_configurations(session):
        indicator_section = sections.setdefault(
            cov_conf.climatic_indicator.identifier,
            schemas.ForecastCoverageNavigationSection(
                climatic_indicator=cov_conf.climatic_indicator,
            ),
        )
        included_model_ids = [fm.id for fm in indicator_section.forecast_models]
        indicator_section.forecast_models.extend(
            fml.forecast_model
            for fml in cov_conf.forecast_model_group.forecast_model_links
            if fml.forecast_model_id not in included_model_ids
        )
        indicator_section.scenarios.extend(
            s for s in cov_conf.scenarios if s not in indicator_section.scenarios
        )
        indicator_section.year_periods.extend(
            yp
            for yp in cov_conf.year_period_group.year_periods
            if yp not in indicator_section.year_periods
        )
        included_time_window_ids = [tw.id for tw in indicator_section.time_windows]
        indicator_section.time_windows.extend(
            twl.forecast_time_window
            for twl in cov_conf.forecast_time_window_links
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


def get_historical_advanced_section_navigation(
    session: sqlmodel.Session,
) -> list[schemas.HistoricalCoverageNavigationSection]:
    sections = {}
    for cov_conf in collect_all_historical_coverage_configurations(session):
        indicator_section = sections.setdefault(
            cov_conf.climatic_indicator.identifier,
            schemas.HistoricalCoverageNavigationSection(
                climatic_indicator=cov_conf.climatic_indicator,
            ),
        )
        indicator_section.year_periods.extend(
            yp
            for yp in cov_conf.year_period_group.year_periods
            if yp not in indicator_section.year_periods
        )
        if (ref_period := cov_conf.reference_period) is not None:
            if ref_period not in indicator_section.reference_periods:
                indicator_section.reference_periods.append(ref_period)
        if (decades := cov_conf.decades) is not None:
            for decade in decades:
                if decade not in indicator_section.decades:
                    indicator_section.decades.append(decade)

    # now sort stuff according to the predefined order
    result = sorted(
        list(sections.values()),
        key=lambda section: (
            section.climatic_indicator.sort_order,
            section.climatic_indicator.measure_type.get_sort_order(),
        ),
    )
    for nav_section in result:
        nav_section: schemas.HistoricalCoverageNavigationSection
        nav_section.year_periods.sort(key=lambda yp: yp.get_sort_order())
        nav_section.decades.sort(key=lambda d: d.get_sort_order())
        nav_section.reference_periods.sort(key=lambda rp: rp.get_sort_order())
    return result
