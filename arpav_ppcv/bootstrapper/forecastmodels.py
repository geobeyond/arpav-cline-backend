from ..schemas import coverages


def generate_forecast_models() -> list[coverages.ForecastModelCreate]:
    return [
        coverages.ForecastModelCreate(
            name="",
            internal_value="",
            coverage_base_path="",
            display_name_english="",
            display_name_italian="",
            description_english="",
            description_italian="",
            sort_order=1,
        ),
    ]
