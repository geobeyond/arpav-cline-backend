from fastapi.responses import JSONResponse


class GeoJsonResponse(JSONResponse):
    media_type = "application/geo+json"
