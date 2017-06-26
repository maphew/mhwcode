https://api.what3words.com/v2/grid?bbox=60.7,-135.0,60.50,-134.75&format=geojson&key=CJD98Y7X


  code	400
  message	"The area covered by 'bbo… parameter is too large"

The area described by the bounding box is too large; the distance between the NE and SW corners should be less than or equal to 2 km.


https://api.what3words.com/v2/grid?bbox=60.67,-135.02,60.68,-135.04&format=geojson&key=CJD98Y7X

Worked better:
https://gist.github.com/maphew/7bb77059574ea714977edae41e4b114c

----
## Goals
The 3x3m grid is often a bit too fine for me. A city lot size is more likely useful. Also I often want to pick the best sounding/looking name in the vicinity.

 * draw selected square
 * draw adjacent squares
 * draw adjacent w3w names in addition to selected

Fetch grid n-by-n around {center}
convert grid to polygons
convert polygons to centroids
d = {}
for c in centroids:
  d.append(reverse geocode(c))
  
for each in d:
  draw each

----
### 2017-June-24

See if commandline ogr2ogr can convert the line grid to polygons. If so we can attempt to use Node.js wrapper of ogr2ogr to do the same.

Doesn't work:
```
D:\...>ogr2ogr -nlt polygon test.shp w3w-grid-schwatka.geojson
ERROR 1: Attempt to write non-polygon (MULTILINESTRING) geometry to POLYGON type shapefile.
ERROR 1: Unable to write feature 0 from layer w3w-grid-schwatka.
ERROR 1: Terminating translation prematurely after failed
translation of layer w3w-grid-schwatka (use -skipfailures to skip errors)
```

This post says it should, https://gis.stackexchange.com/questions/131765/ogr-dxf-closed-polyline-conversion, but maybe these lines are not "closed" in the way ogr needs them to be.

Next attempt: Topojson, Geojson

https://stackoverflow.com/questions/39391746/how-do-you-convert-topojson-linestring-to-polygon
https://stackoverflow.com/questions/40759092/how-to-create-polygon-shape-from-coordinates-returned-by-geojson

60.7,-135.0,60.50,-134.75

Boat launch - 60.672878, -135.024619



