class ArpavError(Exception):
    ...


class InvalidCoverageIdentifierException(ArpavError):
    ...


class CoverageDataRetrievalError(ArpavError):
    ...


class InvalidClimaticIndicatorIdError(ArpavError):
    ...


class InvalidClimaticIndicatorIdentifierError(ArpavError):
    ...


class InvalidObservationStationIdError(ArpavError):
    ...


class InvalidObservationStationCodeError(ArpavError):
    ...


class InvalidObservationSeriesConfigurationIdentifierError(ArpavError):
    ...


class InvalidObservationSeriesConfigurationIdError(ArpavError):
    ...


class InvalidForecastCoverageConfigurationIdentifierError(ArpavError):
    ...


class InvalidForecastCoverageIdentifierError(ArpavError):
    ...


class InvalidForecastCoverageDataSeriesIdentifierError(ArpavError):
    ...


class InvalidSpatialRegionNameError(ArpavError):
    ...


class InvalidForecastYearPeriodError(ArpavError):
    ...


class InvalidForecastModelError(ArpavError):
    ...


class InvalidForecastTimeWindowError(ArpavError):
    ...


class InvalidForecastScenarioError(ArpavError):
    ...


class ObservationInternalNameNotFoundError(ArpavError):
    ...


class ObservationDataRetrievalError(ArpavError):
    ...
