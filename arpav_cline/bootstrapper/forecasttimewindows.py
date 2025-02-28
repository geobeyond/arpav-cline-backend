from ..schemas import coverages


def generate_forecast_time_windows() -> list[coverages.ForecastTimeWindowCreate]:
    return [
        coverages.ForecastTimeWindowCreate(
            name="tw1",
            internal_value="tw1",
            display_name_english="2021-2050",
            display_name_italian="2021-2050",
            description_english="Anomaly 2021-2050 with respect to 1976-2005",
            description_italian="Anomalia 2021-2050 rispetto a 1976-2005",
            sort_order=0,
        ),
        coverages.ForecastTimeWindowCreate(
            name="tw2",
            internal_value="tw2",
            display_name_english="2071-2100",
            display_name_italian="2071-2100",
            description_english="Anomaly 2071-2100 with respect to 1976-2005",
            description_italian="Anomalia 2071-2100 rispetto a 1976-2005",
            sort_order=1,
        ),
    ]
