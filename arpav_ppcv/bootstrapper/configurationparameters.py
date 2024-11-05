from ..schemas.base import CoreConfParamName
from ..schemas.coverages import (
    ConfigurationParameterCreate,
    ConfigurationParameterValueCreateEmbeddedInConfigurationParameter,
)


def generate_configuration_parameters() -> list[ConfigurationParameterCreate]:
    return [
        # ConfigurationParameterCreate(
        #     name=CoreConfParamName.HISTORICAL_VARIABLE.value,
        #     display_name_english="Variable",
        #     display_name_italian="Variabile",
        #     description_english="Historical variable",
        #     description_italian="Variabile storica",
        #     allowed_values=[
        #         ConfigurationParameterValueCreateEmbeddedInConfigurationParameter(
        #             internal_value="tdd",
        #             display_name_english="Average temperature",
        #             display_name_italian="Temperatura media",
        #             description_english="Average of average temperatures",
        #             description_italian="Media delle temperature medie",
        #             sort_order=0,
        #         ),
        #         ConfigurationParameterValueCreateEmbeddedInConfigurationParameter(
        #             internal_value="tnd",
        #             display_name_english="Minimum temperature",
        #             display_name_italian="Temperatura minima",
        #             description_english="Average of minimum temperatures",
        #             description_italian="Media delle temperature minime",
        #             sort_order=0,
        #         ),
        #         ConfigurationParameterValueCreateEmbeddedInConfigurationParameter(
        #             internal_value="txd",
        #             display_name_english="Maximum temperature",
        #             display_name_italian="Temperatura massima",
        #             description_english="Average of maximum temperatures",
        #             description_italian="Media delle temperature massime",
        #             sort_order=0,
        #         ),
        #         ConfigurationParameterValueCreateEmbeddedInConfigurationParameter(
        #             internal_value="tr",
        #             display_name_english="Tropical nights (TR)",
        #             display_name_italian="Notti tropicali (TR)",
        #             description_english=(
        #                 "Number of days with minimum temperature larger than 20°C"
        #             ),
        #             description_italian=(
        #                 "Numero di giorni con temperatura minima maggiore di 20°C"
        #             ),
        #             sort_order=3,
        #         ),
        #         ConfigurationParameterValueCreateEmbeddedInConfigurationParameter(
        #             internal_value="su30",
        #             display_name_english="Summer days (SU30)",
        #             display_name_italian="Giorni caldi (SU30)",
        #             description_english=(
        #                 "Number of days with maximum temperature larger than 30°C"
        #             ),
        #             description_italian=(
        #                 "Numero di giorni con temperatura massima maggiore di 30°C"
        #             ),
        #             sort_order=4,
        #         ),
        #         ConfigurationParameterValueCreateEmbeddedInConfigurationParameter(
        #             internal_value="fd",
        #             display_name_english="Frost days (FD)",
        #             display_name_italian="Giorni di gelo (FD)",
        #             description_english=(
        #                 "Number of days with minimum temperature less than 0°C"
        #             ),
        #             description_italian=(
        #                 "Numero di giorni con temperatura minima minore di 0°C"
        #             ),
        #             sort_order=5,
        #         ),
        #         ConfigurationParameterValueCreateEmbeddedInConfigurationParameter(
        #             internal_value="hdds",
        #             display_name_english="Heating degree days (HDDs)",
        #             display_name_italian="Gradi giorno di riscaldamento (HDDs)",
        #             description_english=(
        #                 "Sum of 20°C minus the average daily temperature if the "
        #                 "average daily temperature is less than 20°C"
        #             ),
        #             description_italian=(
        #                 "Somma di 20°C meno la temperatura media giornaliera se la "
        #                 "temperatura media giornaliera è minore di 20°C"
        #             ),
        #             sort_order=7,
        #         ),
        #         ConfigurationParameterValueCreateEmbeddedInConfigurationParameter(
        #             internal_value="cdds",
        #             display_name_english="Cooling degree days (CDDs)",
        #             display_name_italian="Gradi giorno di raffrescamento (CDDs)",
        #             description_english=(
        #                 "Sum of the average daily temperature minus 21°C if the "
        #                 "average daily temperature is larger than 24°C"
        #             ),
        #             description_italian=(
        #                 "Somma della temperatura media giornaliera meno 21°C se la "
        #                 "temperatura media giornaliera è maggiore di 24°C"
        #             ),
        #             sort_order=8,
        #         ),
        #         ConfigurationParameterValueCreateEmbeddedInConfigurationParameter(
        #             internal_value="prcptot",
        #             display_name_english="Precipitation",
        #             display_name_italian="Precipitazione",
        #             description_english="Daily precipitation near the ground",
        #             description_italian="Precipitazione giornaliera vicino al suolo",
        #             sort_order=0,
        #         ),
        #     ],
        # ),
        # ConfigurationParameterCreate(
        #     name=CoreConfParamName.CLIMATOLOGICAL_VARIABLE.value,
        #     display_name_english="Variable",
        #     display_name_italian="Variabile",
        #     description_english="Climatological variable",
        #     description_italian="Variabile climatologica",
        #     allowed_values=[
        #         ConfigurationParameterValueCreateEmbeddedInConfigurationParameter(
        #             internal_value="cdd",
        #             display_name_english="Consecutive dry days (CDD)",
        #             display_name_italian="Giorni secchi (CDD)",
        #             description_english=(
        #                 "Maximum number of consecutive dry days (daily precipitation "
        #                 "less than 1 mm)"
        #             ),
        #             description_italian=(
        #                 "Numero massimo di giorni consecutivi asciutti "
        #                 "(precipitazione giornaliera inferiore a 1 mm)"
        #             ),
        #             sort_order=11,
        #         ),
        #         ConfigurationParameterValueCreateEmbeddedInConfigurationParameter(
        #             internal_value="cdds",
        #             display_name_english="Cooling degree days (CDDs)",
        #             display_name_italian="Gradi giorno di raffrescamento (CDDs)",
        #             description_english=(
        #                 "Sum of the average daily temperature minus 21°C if the "
        #                 "average daily temperature is larger than 24°C"
        #             ),
        #             description_italian=(
        #                 "Somma della temperatura media giornaliera meno 21°C se la "
        #                 "temperatura media giornaliera è maggiore di 24°C"
        #             ),
        #             sort_order=8,
        #         ),
        #         ConfigurationParameterValueCreateEmbeddedInConfigurationParameter(
        #             internal_value="fd",
        #             display_name_english="Frost days (FD)",
        #             display_name_italian="Giorni di gelo (FD)",
        #             description_english=(
        #                 "Number of days with minimum temperature less than 0ºC"
        #             ),
        #             description_italian=(
        #                 "Numero di giorni con temperatura minima minore di 0°C"
        #             ),
        #             sort_order=5,
        #         ),
        #         ConfigurationParameterValueCreateEmbeddedInConfigurationParameter(
        #             internal_value="hdds",
        #             display_name_english="Heating degree days (HDDs)",
        #             display_name_italian="Gradi giorno di riscaldamento (HDDs)",
        #             description_english=(
        #                 "Sum of 20°C minus the average daily temperature if the "
        #                 "average daily temperature is less than 20°C"
        #             ),
        #             description_italian=(
        #                 "Somma di 20°C meno la temperatura media giornaliera se la "
        #                 "temperatura media giornaliera è minore di 20°C"
        #             ),
        #             sort_order=7,
        #         ),
        #         ConfigurationParameterValueCreateEmbeddedInConfigurationParameter(
        #             internal_value="hwdi",
        #             display_name_english="Heat waves duration index (HWDI)",
        #             display_name_italian="Durata delle ondate di calore (HWDI)",
        #             description_english=(
        #                 "Number of days in which the maximum temperature is 5°C "
        #                 "higher than the average for at least 5 consecutive days"
        #             ),
        #             description_italian=(
        #                 "Numero di giorni in cui la temperatura massima è maggiore "
        #                 "di 5°C rispetto alla media per  almeno 5 giorni consecutivi"
        #             ),
        #             sort_order=6,
        #         ),
        #         ConfigurationParameterValueCreateEmbeddedInConfigurationParameter(
        #             internal_value="pr",
        #             display_name_english="Precipitation (PR)",
        #             display_name_italian="Precipitazione (PR)",
        #             description_english="Daily precipitation near the ground",
        #             description_italian="Precipitazione giornaliera vicino al suolo",
        #             sort_order=9,
        #         ),
        #         ConfigurationParameterValueCreateEmbeddedInConfigurationParameter(
        #             internal_value="r95ptot",
        #             display_name_english="Extreme precipitation (R95pTOT)",
        #             display_name_italian="Precipitazione estrema (R95pTOT)",
        #             description_english=(
        #                 "Total cumulative precipitation above the 95th percentile "
        #                 "with respect to the reference period"
        #             ),
        #             description_italian=(
        #                 "Precipitazione totale cumulata al di sopra del 95o "
        #                 "percentile del periodo di riferimento"
        #             ),
        #             sort_order=10,
        #         ),
        #         ConfigurationParameterValueCreateEmbeddedInConfigurationParameter(
        #             internal_value="snwdays",
        #             display_name_english="Snow days (SNWDAYS)",
        #             display_name_italian="Giorni con neve nuova (SNWDAYS)",
        #             description_english=(
        #                 "Number of days with average temperature less than 2°C and "
        #                 "daily precipitation larger than 1 mm"
        #             ),
        #             description_italian=(
        #                 "Numero di giorni con temperatura media minore di 2°C e "
        #                 "precipitazione giornaliera maggiore di 1 mm"
        #             ),
        #             sort_order=12,
        #         ),
        #         ConfigurationParameterValueCreateEmbeddedInConfigurationParameter(
        #             internal_value="su30",
        #             display_name_english="Summer days (SU30)",
        #             display_name_italian="Giorni caldi (SU30)",
        #             description_english=(
        #                 "Number of days with maximum temperature larger than 30°C"
        #             ),
        #             description_italian=(
        #                 "Numero di giorni con temperatura massima maggiore di 30°C"
        #             ),
        #             sort_order=4,
        #         ),
        #         ConfigurationParameterValueCreateEmbeddedInConfigurationParameter(
        #             internal_value="tas",
        #             display_name_english="Mean temperature (TAS)",
        #             display_name_italian="Temperatura media (TAS)",
        #             description_english=(
        #                 "Daily mean air temperature close to the ground"
        #             ),
        #             description_italian=(
        #                 "Temperatura media giornaliera dell'aria vicino al suolo"
        #             ),
        #             sort_order=0,
        #         ),
        #         ConfigurationParameterValueCreateEmbeddedInConfigurationParameter(
        #             internal_value="tasmax",
        #             display_name_english="Maximum temperature (TASMAX)",
        #             display_name_italian="Temperatura massima (TASMAX)",
        #             description_english=(
        #                 "Daily maximum air temperature close to the ground"
        #             ),
        #             description_italian=(
        #                 "Temperatura massima giornaliera dell'aria vicino al suolo"
        #             ),
        #             sort_order=2,
        #         ),
        #         ConfigurationParameterValueCreateEmbeddedInConfigurationParameter(
        #             internal_value="tasmin",
        #             display_name_english="Minimum temperature (TASMIN)",
        #             display_name_italian="Temperatura minima (TASMIN)",
        #             description_english=(
        #                 "Daily minimum air temperature close to the ground"
        #             ),
        #             description_italian=(
        #                 "Temperatura minima giornaliera dell'aria vicino al suolo"
        #             ),
        #             sort_order=1,
        #         ),
        #         ConfigurationParameterValueCreateEmbeddedInConfigurationParameter(
        #             internal_value="tr",
        #             display_name_english="Tropical nights (TR)",
        #             display_name_italian="Notti tropicali (TR)",
        #             description_english=(
        #                 "Number of days with minimum temperature larger than 20°C"
        #             ),
        #             description_italian=(
        #                 "Numero di giorni con temperatura minima maggiore di 20°C"
        #             ),
        #             sort_order=3,
        #         ),
        #     ],
        # ),
        ConfigurationParameterCreate(
            name=CoreConfParamName.SCENARIO.value,
            display_name_english="Scenario",
            display_name_italian="Scenario",
            description_english="Climate model scenario",
            description_italian="Scenario del modello climatico",
            allowed_values=[
                ConfigurationParameterValueCreateEmbeddedInConfigurationParameter(
                    internal_value="rcp26",
                    display_name_english="RCP2.6",
                    display_name_italian="RCP2.6",
                    description_english=(
                        "Strong greenhouse gas emissions mitigation scenario"
                    ),
                    description_italian=(
                        "Scenario forte mitigazione emissioni gas serra"
                    ),
                    sort_order=0,
                ),
                ConfigurationParameterValueCreateEmbeddedInConfigurationParameter(
                    internal_value="rcp45",
                    display_name_english="RCP4.5",
                    display_name_italian="RCP4.5",
                    description_english="Stabilization scenario",
                    description_italian="Scenario intermedio di stabilizzazione",
                    sort_order=1,
                ),
                ConfigurationParameterValueCreateEmbeddedInConfigurationParameter(
                    internal_value="rcp85",
                    display_name_english="RCP8.5",
                    display_name_italian="RCP8.5",
                    description_english="No mitigation scenario",
                    description_italian="Scenario nessuna mitigazione",
                    sort_order=2,
                ),
            ],
        ),
        ConfigurationParameterCreate(
            name="time_window",
            display_name_english="Time window",
            display_name_italian="Finestra temporale",
            description_english="",
            description_italian="",
            allowed_values=[
                ConfigurationParameterValueCreateEmbeddedInConfigurationParameter(
                    internal_value="tw1",
                    display_name_english="2021-2050",
                    display_name_italian="2021-2050",
                    description_english="Anomaly 2021-2050 with respect to 1976-2005",
                    description_italian="Anomalia 2021-2050 rispetto a 1976-2005",
                    sort_order=0,
                ),
                ConfigurationParameterValueCreateEmbeddedInConfigurationParameter(
                    internal_value="tw2",
                    display_name_english="2071-2100",
                    display_name_italian="2071-2100",
                    description_english="Anomaly 2071-2100 with respect to 1976-2005",
                    description_italian="Anomalia 2071-2100 rispetto a 1976-2005",
                    sort_order=1,
                ),
            ],
        ),
        ConfigurationParameterCreate(
            name=CoreConfParamName.YEAR_PERIOD.value,
            display_name_english="Year period",
            display_name_italian="Periodo dell'anno",
            description_english="Yearly temporal aggregation period",
            description_italian="Periodo di aggregazione temporale annuale",
            allowed_values=[
                ConfigurationParameterValueCreateEmbeddedInConfigurationParameter(
                    name="winter",
                    internal_value="DJF",
                    display_name_english="Winter",
                    display_name_italian="Inverno",
                    description_english="December, January, February",
                    description_italian="Dicembre, gennaio, febbraio",
                    sort_order=4,
                ),
                ConfigurationParameterValueCreateEmbeddedInConfigurationParameter(
                    name="spring",
                    internal_value="MAM",
                    display_name_english="Spring",
                    display_name_italian="Primavera",
                    description_english="March, April, May",
                    description_italian="Marzo, aprile, maggio",
                    sort_order=1,
                ),
                ConfigurationParameterValueCreateEmbeddedInConfigurationParameter(
                    name="summer",
                    internal_value="JJA",
                    display_name_english="Summer",
                    display_name_italian="Estate",
                    description_english="June, July, August",
                    description_italian="Giugno, luglio, agosto",
                    sort_order=2,
                ),
                ConfigurationParameterValueCreateEmbeddedInConfigurationParameter(
                    name="autumn",
                    internal_value="SON",
                    display_name_english="Autumn",
                    display_name_italian="Autunno",
                    description_english="September, October, November",
                    description_italian="Settembre, ottobre, novembre",
                    sort_order=3,
                ),
                ConfigurationParameterValueCreateEmbeddedInConfigurationParameter(
                    internal_value="year",
                    name="all_year",
                    display_name_english="Year",
                    display_name_italian="Anno",
                    description_english="Solar year (from January to December)",
                    description_italian="Anno solare (da gennaio a dicembre)",
                    sort_order=0,
                ),
            ],
        ),
        ConfigurationParameterCreate(
            name=CoreConfParamName.HISTORICAL_YEAR_PERIOD.value,
            display_name_english="year period - historical data",
            display_name_italian="periodo dell'anno - dati storici",
            description_english="Yearly temporal aggregation period for historical data",
            description_italian=(
                "Periodo di aggregazione temporale annuale per i dati storici"
            ),
            allowed_values=[
                ConfigurationParameterValueCreateEmbeddedInConfigurationParameter(
                    internal_value="S01",
                    name="winter",
                    display_name_english="Winter",
                    display_name_italian="Inverno",
                    description_english="Winter season",
                    description_italian="Stagione invernale",
                    sort_order=4,
                ),
                ConfigurationParameterValueCreateEmbeddedInConfigurationParameter(
                    internal_value="S02",
                    name="spring",
                    display_name_english="Spring",
                    display_name_italian="Primavera",
                    description_english="Spring season",
                    description_italian="Stagione primaverile",
                    sort_order=1,
                ),
                ConfigurationParameterValueCreateEmbeddedInConfigurationParameter(
                    internal_value="S03",
                    name="summer",
                    display_name_english="Summer",
                    display_name_italian="Estate",
                    description_english="Summer season",
                    description_italian="Stagione estiva",
                    sort_order=2,
                ),
                ConfigurationParameterValueCreateEmbeddedInConfigurationParameter(
                    internal_value="S04",
                    name="autumn",
                    display_name_english="Autumn",
                    display_name_italian="Autunno",
                    description_english="Autumn season",
                    description_italian="Stagione autunnale",
                    sort_order=3,
                ),
                ConfigurationParameterValueCreateEmbeddedInConfigurationParameter(
                    internal_value="A00",
                    name="all_year",
                    display_name_english="Year",
                    display_name_italian="Anno",
                    description_english="Solar year (from January to December)",
                    description_italian="Anno solare (da gennaio a dicembre)",
                    sort_order=0,
                ),
                ConfigurationParameterValueCreateEmbeddedInConfigurationParameter(
                    internal_value="M01",
                    name="january",
                    display_name_english="January",
                    display_name_italian="Gennaio",
                    description_english="Month of January",
                    description_italian="mese di gennaio",
                    sort_order=0,
                ),
                ConfigurationParameterValueCreateEmbeddedInConfigurationParameter(
                    internal_value="M02",
                    name="february",
                    display_name_english="February",
                    display_name_italian="Febbraio",
                    description_english="Month of february",
                    description_italian="mese di febbraio",
                    sort_order=0,
                ),
                ConfigurationParameterValueCreateEmbeddedInConfigurationParameter(
                    internal_value="M03",
                    name="march",
                    display_name_english="March",
                    display_name_italian="Marzo",
                    description_english="Month of march",
                    description_italian="mese di marzo",
                    sort_order=0,
                ),
                ConfigurationParameterValueCreateEmbeddedInConfigurationParameter(
                    internal_value="M04",
                    name="april",
                    display_name_english="April",
                    display_name_italian="Aprile",
                    description_english="Month of april",
                    description_italian="mese di aprile",
                    sort_order=0,
                ),
                ConfigurationParameterValueCreateEmbeddedInConfigurationParameter(
                    internal_value="M05",
                    name="may",
                    display_name_english="May",
                    display_name_italian="Maggio",
                    description_english="Month of may",
                    description_italian="mese di maggio",
                    sort_order=0,
                ),
                ConfigurationParameterValueCreateEmbeddedInConfigurationParameter(
                    internal_value="M06",
                    name="june",
                    display_name_english="June",
                    display_name_italian="Giugno",
                    description_english="Month of sune",
                    description_italian="mese di giugno",
                    sort_order=0,
                ),
                ConfigurationParameterValueCreateEmbeddedInConfigurationParameter(
                    internal_value="M07",
                    name="july",
                    display_name_english="July",
                    display_name_italian="Luglio",
                    description_english="Month of july",
                    description_italian="mese di luglio",
                    sort_order=0,
                ),
                ConfigurationParameterValueCreateEmbeddedInConfigurationParameter(
                    internal_value="M08",
                    name="august",
                    display_name_english="August",
                    display_name_italian="Agosto",
                    description_english="Month of august",
                    description_italian="mese di agosto",
                    sort_order=0,
                ),
                ConfigurationParameterValueCreateEmbeddedInConfigurationParameter(
                    internal_value="M09",
                    name="september",
                    display_name_english="September",
                    display_name_italian="Settembre",
                    description_english="Month of september",
                    description_italian="mese di settembre",
                    sort_order=0,
                ),
                ConfigurationParameterValueCreateEmbeddedInConfigurationParameter(
                    internal_value="M10",
                    name="october",
                    display_name_english="October",
                    display_name_italian="Ottobre",
                    description_english="Month of october",
                    description_italian="mese di ottobre",
                    sort_order=0,
                ),
                ConfigurationParameterValueCreateEmbeddedInConfigurationParameter(
                    internal_value="M11",
                    name="november",
                    display_name_english="November",
                    display_name_italian="Novembre",
                    description_english="Month of november",
                    description_italian="mese di novembre",
                    sort_order=0,
                ),
                ConfigurationParameterValueCreateEmbeddedInConfigurationParameter(
                    internal_value="M12",
                    name="december",
                    display_name_english="December",
                    display_name_italian="Dicembre",
                    description_english="Month of december",
                    description_italian="mese di dicembre",
                    sort_order=0,
                ),
            ],
        ),
        # ConfigurationParameterCreate(
        #     name=CoreConfParamName.MEASURE.value,
        #     display_name_english="Measurement type",
        #     display_name_italian="Tipo di misurazione",
        #     description_english="Type of climatological measurement",
        #     description_italian="Tipo di misurazione climatologica",
        #     allowed_values=[
        #         ConfigurationParameterValueCreateEmbeddedInConfigurationParameter(
        #             internal_value="absolute",
        #             display_name_english="Absolute value",
        #             display_name_italian="Valore assoluto",
        #             description_english="Actual value in the selected period",
        #             description_italian="Valore effettivo nel periodo selezionato",
        #             sort_order=0,
        #         ),
        #         ConfigurationParameterValueCreateEmbeddedInConfigurationParameter(
        #             internal_value="anomaly",
        #             display_name_english="Anomaly",
        #             display_name_italian="Anomalia",
        #             description_english=(
        #                 "Change in the future with respect to the reference period"
        #             ),
        #             description_italian=(
        #                 "Variazione nel futuro rispetto al periodo di riferimento"
        #             ),
        #             sort_order=1,
        #         ),
        #     ],
        # ),
        ConfigurationParameterCreate(
            name=CoreConfParamName.CLIMATOLOGICAL_MODEL.value,
            display_name_english="Forecast model",
            display_name_italian="Modello di previsione",
            description_english=(
                "Numerical model used to generate climatological forecast datasets"
            ),
            description_italian=(
                "Modello numerico utilizzato per generare set di dati di previsione "
                "climatologica"
            ),
            allowed_values=[
                ConfigurationParameterValueCreateEmbeddedInConfigurationParameter(
                    internal_value="model_ensemble",
                    display_name_english="Ensemble mean",
                    display_name_italian="Media ensemble",
                    description_english="Ensemble mean of five considered models",
                    description_italian="Media ensemble 5 modelli considerati",
                    sort_order=0,
                ),
                ConfigurationParameterValueCreateEmbeddedInConfigurationParameter(
                    internal_value="ec_earth_cclm_4_8_17",
                    display_name_english="EC-EARTH_CCLM4-8-17",
                    display_name_italian="EC-EARTH_CCLM4-8-17",
                    description_english="Global: EC-EARTH. Regional: CCLM4-8-17",
                    description_italian="Globale: EC-EARTH. Regionale: CCLM4-8-17",
                    sort_order=1,
                ),
                ConfigurationParameterValueCreateEmbeddedInConfigurationParameter(
                    internal_value="ec_earth_racmo22e",
                    display_name_english="EC-EARTH_RACMO22E",
                    display_name_italian="EC-EARTH_RACMO22E",
                    description_english="Global: EC-EARTH. Regional: RACMO22E",
                    description_italian="Globale: EC-EARTH. Regionale: RACMO22E",
                    sort_order=2,
                ),
                ConfigurationParameterValueCreateEmbeddedInConfigurationParameter(
                    internal_value="ec_earth_rca4",
                    display_name_english="EC-EARTH_RCA4",
                    display_name_italian="EC-EARTH_RCA4",
                    description_english="Global: EC-EARTH. Regional: RCA4",
                    description_italian="Globale EC-EARTH. Regionale: RCA4",
                    sort_order=3,
                ),
                ConfigurationParameterValueCreateEmbeddedInConfigurationParameter(
                    internal_value="hadgem2_racmo22e",
                    display_name_english="HadGEM2-ES_RACMO22E",
                    display_name_italian="HadGEM2-ES_RACMO22E",
                    description_english="Global: HadGEM2-ES. Regional: RACMO22E",
                    description_italian="Globale: HadGEM2-ES. Regionale: RACMO22E",
                    sort_order=4,
                ),
                ConfigurationParameterValueCreateEmbeddedInConfigurationParameter(
                    internal_value="mpi_esm_lr_remo2009",
                    display_name_english="MPI-ESM-LR_REMO2009",
                    display_name_italian="MPI-ESM-LR_REMO2009",
                    description_english="Global: MPI-ESM-LR. Regional: REMO2009",
                    description_italian="Globale: MPI-ESM-LR. Regionale: REMO2009",
                    sort_order=5,
                ),
            ],
        ),
        # ConfigurationParameterCreate(
        #     name=CoreConfParamName.AGGREGATION_PERIOD.value,
        #     display_name_english="Temporal aggregation period",
        #     display_name_italian="Periodo di aggregazione temporale",
        #     description_english="Aggregation period for climatological datasets",
        #     description_italian="Periodo di aggregazione per i set di dati climatologici",
        #     allowed_values=[
        #         ConfigurationParameterValueCreateEmbeddedInConfigurationParameter(
        #             internal_value="30yr",
        #             display_name_english="30-year",
        #             display_name_italian="Trentennale",
        #             description_english="Average over the selected 30-year period",
        #             description_italian="Media sul trentennio selezionato",
        #             sort_order=1,
        #         ),
        #         ConfigurationParameterValueCreateEmbeddedInConfigurationParameter(
        #             internal_value="annual",
        #             display_name_english="Annual",
        #             display_name_italian="Annuale",
        #             description_english="Average over the selected year",
        #             description_italian="Media sull'anno selezionato",
        #             sort_order=0,
        #         ),
        #     ],
        # ),
        ConfigurationParameterCreate(
            name=CoreConfParamName.UNCERTAINTY_TYPE.value,
            display_name_english="Uncertainty type",
            display_name_italian="Tipologia dei limiti di incertezza",
            description_english="Type of uncertainty that this configuration represents",
            description_italian="Tipo di incertezza che questa configurazione rappresenta",
            allowed_values=[
                ConfigurationParameterValueCreateEmbeddedInConfigurationParameter(
                    internal_value="upper_bound",
                    display_name_english="Uncertainty upper bounds",
                    display_name_italian="Limiti superiori dell'incertezza",
                    description_english=(
                        "Dataset contains upper bound uncertainty-related values"
                    ),
                    description_italian=(
                        "Il set di dati contiene valori relativi all'incertezza del "
                        "limite superiore"
                    ),
                    sort_order=0,
                ),
                ConfigurationParameterValueCreateEmbeddedInConfigurationParameter(
                    internal_value="lower_bound",
                    display_name_english="Uncertainty lower bounds",
                    display_name_italian="Limiti inferiori dell'incertezza",
                    description_english=(
                        "Dataset contains lower bound uncertainty-related values"
                    ),
                    description_italian=(
                        "Il set di dati contiene valori relativi all'incertezza del "
                        "limite inferiore"
                    ),
                    sort_order=0,
                ),
            ],
        ),
        ConfigurationParameterCreate(
            name=CoreConfParamName.ARCHIVE.value,
            display_name_english="Dataset archive",
            display_name_italian="archivio di dataset",
            description_english="The archive that the dataset belongs to",
            description_italian="L'archivio a cui appartiene il set di dati",
            allowed_values=[
                ConfigurationParameterValueCreateEmbeddedInConfigurationParameter(
                    internal_value="historical",
                    display_name_english="Historical data",
                    display_name_italian="Dati storici",
                    description_english=("Datasets obtained from historical data"),
                    description_italian=("Set di dati ottenuti da dati storici"),
                    sort_order=0,
                ),
                ConfigurationParameterValueCreateEmbeddedInConfigurationParameter(
                    internal_value="forecast",
                    display_name_english="Forecast data",
                    display_name_italian="Dati di previsione",
                    description_english=("Datasets obtained from forecasts"),
                    description_italian=("Set di dati ottenuti dalle previsioni"),
                    sort_order=0,
                ),
                ConfigurationParameterValueCreateEmbeddedInConfigurationParameter(
                    internal_value="barometro_climatico",
                    display_name_english="Climate barometer",
                    display_name_italian="Barometro climatico",
                    description_english="Regional overview",
                    description_italian="Panoramica regionale",
                    sort_order=0,
                ),
            ],
        ),
        ConfigurationParameterCreate(
            name="climatological_standard_normal",
            display_name_english="Climatological standard normal",
            display_name_italian="Standard climatologico normale",
            description_english="Standard climatological normal periods",
            description_italian="Periodi normali climatologici standard",
            allowed_values=[
                ConfigurationParameterValueCreateEmbeddedInConfigurationParameter(
                    internal_value="1981-2010",
                    display_name_english="CN 1981-2010",
                    display_name_italian="CN 1981-2010",
                    description_english=(
                        "Climatological standard normal for the period 1981-2010"
                    ),
                    description_italian=(
                        "Normale standard climatologica per il periodo 1981-2010"
                    ),
                    sort_order=0,
                ),
                ConfigurationParameterValueCreateEmbeddedInConfigurationParameter(
                    internal_value="1991-2020",
                    display_name_english="CN 1991-2020",
                    display_name_italian="CN 1991-2020",
                    description_english=(
                        "Climatological standard normal for the period 1991-2020"
                    ),
                    description_italian=(
                        "Normale standard climatologica per il periodo 1991-2020"
                    ),
                    sort_order=0,
                ),
                ConfigurationParameterValueCreateEmbeddedInConfigurationParameter(
                    internal_value="2001-2030",
                    display_name_english="CN 2001-2030",
                    display_name_italian="CN 2001-2030",
                    description_english=(
                        "Climatological standard normal for the period 2001-2030"
                    ),
                    description_italian=(
                        "Normale standard climatologica per il periodo 2001-2030"
                    ),
                    sort_order=0,
                ),
            ],
        ),
    ]
