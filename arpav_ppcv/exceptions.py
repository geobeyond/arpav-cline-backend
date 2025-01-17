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


class InvalidObservationSeriesConfigurationIdentifierError(ArpavError):
    ...


class InvalidForecastCoverageConfigurationIdentifierError(ArpavError):
    ...


class InvalidForecastCoverageIdentifierError(ArpavError):
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
