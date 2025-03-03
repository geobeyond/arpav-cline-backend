import enum


class PrefectTaskTag(enum.Enum):
    USES_DB = "uses_db"
    USES_EXTERNAL_REST_API = "uses_external_rest_api"
    USES_ARPA_V_REST_API = "uses_arpa_v_rest_api"
    USES_ARPA_FVG_REST_API = "uses_arpa_fvg_rest_api"
