# ARPAV-PPCV auxiliary datasets


### Italian municipalities

The `municipalities-istat-2021.geojson` file holds a dataset with italian municipalities that are part of the
relevant regions for the ARPAV-PPCV system, namely:

- Friuli Venezia Giulia
- Trentino-Alto Adige
- Veneto

The ARPAV-PPCV system expects each municipality feature to have the following properties:

- `fid`
- `name`
- `province_name`
- `region_name`
- `xcoord` - longitude of the centroid, in EPSG:4326
- `ycoord` - latitude of the centroid, in EPSG:4326

The system also expects features to have a geometry type of `MultiPolygon`


This dataset has been prepared from the official ISTAT datasets, which are made available publicly at:

    https://www.istat.it/notizia/confini-delle-unita-amministrative-a-fini-statistici-al-1-gennaio-2018-2/

The dataset currently in use is the one for the year 2021. This was chosen as this was the latest bundle which
included the relevant centroid information for each municipality in the companion .xlsx file.

The original downloaded dataset consisted of a zingle zip file which decompressed into multiple files, for which the
following were relevant:

- ProvCM2021/ProvCM2021.sh* - geospatial boundaries of all italian municipalities
- ElencoUnitaAmministrative2021.xlsx - relevant alphanumerical information about municipalities, including the
  coordinates of the points which should be regarded as the centroid

The original dataset was pre-processed into the `municipalities-istat-2021.geojson` present in this directory.
Pre-processing consisted mainly in the following operations:

- Discard all municipalities which do not belong to the any of the target regions
- Include the name of the province and the name of the region for each municipality
- Extract the x and y coordinates from the .xlsx which represent municipality centroids and join them with the
  respective municipality
- Reproject the geometries and also the x and and y coordinates of centroids to `EPSG:4326`
- Save the result as a GeoJSON file

This dataset is ingested into the ARPAV-PPCV system database by running the command:

```shell
arpav-ppcv bootstrap municipalities data/municipalities-istat-2021.geojson
```
