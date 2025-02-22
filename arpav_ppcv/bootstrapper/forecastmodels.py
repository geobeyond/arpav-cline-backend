from ..schemas import coverages


def generate_forecast_models() -> list[coverages.ForecastModelCreate]:
    return [
        coverages.ForecastModelCreate(
            name="model_ensemble",
            internal_value="model_ensemble",
            display_name_english="Ensemble mean",
            display_name_italian="Media ensemble",
            description_english="Ensemble mean of five considered models",
            description_italian="Media ensemble 5 modelli considerati",
            sort_order=0,
        ),
        coverages.ForecastModelCreate(
            name="ec_earth_cclm_4_8_17",
            internal_value="EC-EARTH_CCLM4-8-17",
            display_name_english="EC-EARTH_CCLM4-8-17",
            display_name_italian="EC-EARTH_CCLM4-8-17",
            description_english="Global: EC-EARTH. Regional: CCLM4-8-17",
            description_italian="Globale: EC-EARTH. Regionale: CCLM4-8-17",
            sort_order=1,
        ),
        coverages.ForecastModelCreate(
            name="ec_earth_racmo22e",
            internal_value="EC-EARTH_RACMO22E",
            display_name_english="EC-EARTH_RACMO22E",
            display_name_italian="EC-EARTH_RACMO22E",
            description_english="Global: EC-EARTH. Regional: RACMO22E",
            description_italian="Globale: EC-EARTH. Regionale: RACMO22E",
            sort_order=2,
        ),
        coverages.ForecastModelCreate(
            name="ec_earth_rca4",
            internal_value="EC-EARTH_RCA4",
            display_name_english="EC-EARTH_RCA4",
            display_name_italian="EC-EARTH_RCA4",
            description_english="Global: EC-EARTH. Regional: RCA4",
            description_italian="Globale: EC-EARTH. Regionale: RCA4",
            sort_order=3,
        ),
        coverages.ForecastModelCreate(
            name="hadgem2_racmo22e",
            internal_value="HadGEM2-ES_RACMO22E",
            display_name_english="HadGEM2-ES_RACMO22E",
            display_name_italian="HadGEM2-ES_RACMO22E",
            description_english="Global: HadGEM2-ES. Regional: RACMO22E",
            description_italian="Globale: HadGEM2-ES. Regionale: RACMO22E",
            sort_order=4,
        ),
        coverages.ForecastModelCreate(
            name="mpi_esm_lr_remo2009",
            internal_value="MPI-ESM-LR_REMO2009",
            display_name_english="MPI-ESM-LR_REMO2009",
            display_name_italian="MPI-ESM-LR_REMO2009",
            description_english="Global: MPI-ESM-LR. Regional: REMO2009",
            description_italian="Globale: MPI-ESM-LR. Regionale: REMO2009",
            sort_order=5,
        ),
    ]


def generate_forecast_model_groups(
    forecast_model_ids: dict[str, int],
) -> list[coverages.ForecastModelGroupCreate]:
    return [
        coverages.ForecastModelGroupCreate(
            name="ensemble",
            display_name_english="Ensemble",
            display_name_italian="Insieme",
            description_english="Ensemble description",
            description_italian="descrizione dell'insieme",
            sort_order=0,
            forecast_models=[forecast_model_ids["model_ensemble"]],
        ),
        coverages.ForecastModelGroupCreate(
            name="five_models",
            display_name_english="Five models",
            display_name_italian="Cinque modelli",
            description_english="Five models description",
            description_italian="descrizione dei cinque modelli",
            sort_order=0,
            forecast_models=[
                forecast_model_ids["ec_earth_cclm_4_8_17"],
                forecast_model_ids["ec_earth_racmo22e"],
                forecast_model_ids["ec_earth_rca4"],
                forecast_model_ids["hadgem2_racmo22e"],
                forecast_model_ids["mpi_esm_lr_remo2009"],
            ],
        ),
    ]
