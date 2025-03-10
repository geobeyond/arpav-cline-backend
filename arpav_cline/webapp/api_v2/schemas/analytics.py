import datetime as dt
import pydantic


class TimeSeriesDownloadRequestRead(pydantic.BaseModel):
    request_datetime: dt.datetime
    entity_name: str | None
    is_public_sector: bool
    download_reason: str
    climatological_variable: str
    aggregation_period: str
    measure_type: str
    year_period: str
    data_category: str
    longitude: float
    latitude: float
