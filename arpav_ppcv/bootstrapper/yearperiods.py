from ..schemas.coverages import (
    ForecastYearPeriodGroupCreate,
    HistoricalYearPeriodGroupCreate,
)
from ..schemas.static import (
    HistoricalYearPeriod,
    ForecastYearPeriod,
)


def generate_forecast_year_period_groups() -> list[ForecastYearPeriodGroupCreate]:
    return [
        ForecastYearPeriodGroupCreate(
            name="only_year",
            display_name_english="Only year",
            display_name_italian="Solo anno",
            description_english="Only year description",
            description_italian="Solo descrizione dell'anno",
            sort_order=0,
            year_periods=[
                ForecastYearPeriod.ALL_YEAR,
            ],
        ),
        ForecastYearPeriodGroupCreate(
            name="all_seasons",
            display_name_english="All seasons",
            display_name_italian="Tutte le stagioni",
            description_english="All seasons description",
            description_italian="Descrizione di tutte le stagioni",
            sort_order=1,
            year_periods=[
                ForecastYearPeriod.WINTER,
                ForecastYearPeriod.SPRING,
                ForecastYearPeriod.SUMMER,
                ForecastYearPeriod.AUTUMN,
            ],
        ),
        ForecastYearPeriodGroupCreate(
            name="only_summer",
            display_name_english="Only summer",
            display_name_italian="Solo estate",
            description_english="Only summer description",
            description_italian="Solo estate descrizione",
            sort_order=2,
            year_periods=[
                ForecastYearPeriod.SUMMER,
            ],
        ),
    ]


def generate_historical_year_period_groups() -> list[HistoricalYearPeriodGroupCreate]:
    return [
        HistoricalYearPeriodGroupCreate(
            name="only_year",
            display_name_english="Only year",
            display_name_italian="Solo anno",
            description_english="Only year description",
            description_italian="Solo descrizione dell'anno",
            sort_order=0,
            year_periods=[
                HistoricalYearPeriod.ALL_YEAR,
            ],
        ),
        HistoricalYearPeriodGroupCreate(
            name="all_seasons",
            display_name_english="All seasons",
            display_name_italian="Tutte le stagioni",
            description_english="All seasons description",
            description_italian="Descrizione di tutte le stagioni",
            sort_order=1,
            year_periods=[
                HistoricalYearPeriod.WINTER,
                HistoricalYearPeriod.SPRING,
                HistoricalYearPeriod.SUMMER,
                HistoricalYearPeriod.AUTUMN,
            ],
        ),
        HistoricalYearPeriodGroupCreate(
            name="all_months",
            display_name_english="All months",
            display_name_italian="Tutti i mesi",
            description_english="All seasons description",
            description_italian="Descrizione di tutti i mesi",
            sort_order=2,
            year_periods=[
                HistoricalYearPeriod.JANUARY,
                HistoricalYearPeriod.FEBRUARY,
                HistoricalYearPeriod.MARCH,
                HistoricalYearPeriod.APRIL,
                HistoricalYearPeriod.MAY,
                HistoricalYearPeriod.JUNE,
                HistoricalYearPeriod.JULY,
                HistoricalYearPeriod.AUGUST,
                HistoricalYearPeriod.SEPTEMBER,
                HistoricalYearPeriod.OCTOBER,
                HistoricalYearPeriod.NOVEMBER,
                HistoricalYearPeriod.DECEMBER,
            ],
        ),
        HistoricalYearPeriodGroupCreate(
            name="all_periods",
            display_name_english="All periods",
            display_name_italian="Tutti i periodi",
            description_english="All periods description",
            description_italian="Tutti i periodi descrizzione",
            sort_order=3,
            year_periods=[
                HistoricalYearPeriod.ALL_YEAR,
                HistoricalYearPeriod.WINTER,
                HistoricalYearPeriod.SPRING,
                HistoricalYearPeriod.SUMMER,
                HistoricalYearPeriod.AUTUMN,
                HistoricalYearPeriod.JANUARY,
                HistoricalYearPeriod.FEBRUARY,
                HistoricalYearPeriod.MARCH,
                HistoricalYearPeriod.APRIL,
                HistoricalYearPeriod.MAY,
                HistoricalYearPeriod.JUNE,
                HistoricalYearPeriod.JULY,
                HistoricalYearPeriod.AUGUST,
                HistoricalYearPeriod.SEPTEMBER,
                HistoricalYearPeriod.OCTOBER,
                HistoricalYearPeriod.NOVEMBER,
                HistoricalYearPeriod.DECEMBER,
            ],
        ),
    ]
