import enum
import pydantic
import sqlmodel


class Season(enum.Enum):
    WINTER = "WINTER"
    SPRING = "SPRING"
    SUMMER = "SUMMER"
    AUTUMN = "AUTUMN"


class ObservationDataSmoothingStrategy(enum.Enum):
    MOVING_AVERAGE_5_YEARS = "MOVING_AVERAGE_5_YEARS"


class ObservationAggregationType(enum.Enum):
    MONTHLY = "MONTHLY"
    SEASONAL = "SEASONAL"
    YEARLY = "YEARLY"


class CoverageDataSmoothingStrategy(enum.Enum):
    MOVING_AVERAGE_11_YEARS_PLUS_LOESS_SMOOTHING = "MOVING_AVERAGE_11_YEARS_PLUS_LOESS_SMOOTHING"


class ResourceList(pydantic.BaseModel):
    items: list[sqlmodel.SQLModel]
