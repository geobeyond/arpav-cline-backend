from ..schemas.observations import VariableCreate


def generate_variable_configurations() -> list[VariableCreate]:
    return [
        VariableCreate(
            name="HDD_it",
            display_name_english="Heating degree days",
            display_name_italian="Gradi giorno di riscaldamento",
            description_english=("Heating degree days, with Tbase 20 °C for Tavg"),
            description_italian=(
                "Gradi giorno di riscaldamento, con Tbase 20 °C per Tavg"
            ),
            unit_english="ºC",
        ),
        VariableCreate(
            name="CDD_jrc",
            display_name_english="Cooling degree days",
            display_name_italian="Gradi giorno di raffrescamento",
            description_english=(
                "Cooling degree days, with Tbase 21 °C and threshold 24 °C for Tavg"
            ),
            description_italian=(
                "Gradi giorno di raffrescamento, con Tbase 21 °C e soglia 24 °C per Tavg"
            ),
            unit_english="ºC",
        ),
        VariableCreate(
            name="TDd",
            display_name_english="Mean temperature (from observation station)",
            display_name_italian="Temperatura media (dalla stazione di osservazione)",
            description_english="Average daily air temperature near the ground",
            description_italian=(
                "Temperatura media giornaliera dell'aria vicino al suolo"
            ),
            unit_english="ºC",
        ),
        VariableCreate(
            name="TXd",
            display_name_english="Max temperature (from observation station)",
            display_name_italian="Temperatura massima (dalla stazione di osservazione)",
            description_english="Maximum daily air temperature near the ground",
            description_italian=(
                "Temperatura massima giornaliera dell'aria vicino al suolo"
            ),
            unit_english="ºC",
        ),
        VariableCreate(
            name="TNd",
            display_name_english="Minimum temperature (from observation station)",
            display_name_italian="Temperatura minima (dalla stazione di osservazione)",
            description_english="Minimum daily air temperature near the ground",
            description_italian=(
                "Temperatura minima giornaliera dell'aria vicino al suolo"
            ),
            unit_english="ºC",
        ),
        VariableCreate(
            name="PRCPTOT",
            display_name_english="Precipitation (from observation station)",
            display_name_italian="Precipitazione (dalla stazione di osservazione)",
            description_english="Daily precipitation near the ground",
            description_italian="Precipitazioni giornaliere in prossimità del suolo",
            unit_english="mm",
        ),
        VariableCreate(
            name="TR",
            display_name_english="Tropical nights (from observation station)",
            display_name_italian="Notti tropicali (dalla stazione di osservazione)",
            description_english=(
                "Number of days with minimum temperature greater than 20 °C"
            ),
            description_italian=(
                "Numero di giorni con temperatura minima superiore a 20 °C"
            ),
            unit_english="days",
            unit_italian="giorni",
        ),
        VariableCreate(
            name="SU30",
            display_name_english="Hot days (from observation station)",
            display_name_italian="Giorni caldi (dalla stazione di osservazione)",
            description_english=(
                "Number of days with maximum temperature greater than 30 °C"
            ),
            description_italian=(
                "Numero di giorni con temperatura massima superiore a 30 °C"
            ),
            unit_english="days",
            unit_italian="giorni",
        ),
        VariableCreate(
            name="FD",
            display_name_english="Frosty days (from observation station)",
            display_name_italian="Giorni di gelo (dalla stazione di osservazione)",
            description_english=(
                "Number of days with minimum temperature less than 0 °C"
            ),
            description_italian=(
                "Numero di giorni con temperatura minima inferiore a 0 °C"
            ),
            unit_english="days",
            unit_italian="giorni",
        ),
    ]
