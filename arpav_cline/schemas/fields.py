import json
from typing import Annotated

import geoalchemy2
import shapely.io
from pydantic.functional_serializers import PlainSerializer


def serialize_wkbelement(wkbelement: geoalchemy2.WKBElement):
    geom = shapely.io.from_wkb(bytes(wkbelement.data))
    return json.loads(shapely.io.to_geojson(geom))


WkbElement = Annotated[
    geoalchemy2.WKBElement,
    PlainSerializer(serialize_wkbelement, return_type=dict, when_used="json"),
]
