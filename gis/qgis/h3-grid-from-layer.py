# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "h3",
# ]
# ///

"""Generate an h3 index grid from the extents of input layer.
In Qgis:
    Processing Toolbox >> Open existing script >> {select this file}
        >> Select template extent layer in table of contents
            >> optionally select specific features to get extent from
        >> Edit the variables below (particularly min/max)
        >> Run

Adapted from:
 - https://github.com/ThomasG77/30DayMapChallenge/blob/master/day4_hexagons/data/h3-processing.py
 - https://gis.stackexchange.com/questions/310555/using-uber-h3-from-qgis/
License: X/MIT
(c) 2021 matt wilkie <maphew@gmail.com>
"""
import os
from qgis.utils import iface
from qgis.core import (
    QgsCoordinateReferenceSystem,
    QgsCoordinateTransform,
    QgsFeature,
    QgsField,
    QgsFields,
    QgsGeometry,
    QgsPointXY,
    QgsProject,
    QgsProcessingFeedback,
    QgsMessageLog,
    QgsVectorFileWriter,
    QgsVectorLayer,
    QgsWkbTypes,
)
from qgis.PyQt.QtCore import QVariant
import processing
import h3

debug = False

###---------- Edit these variables ----------
# Min & max h3 resolution levels, from 0 to 15 (global to sub-meter)
# High resolutions over broad areas can be slow and consume a lot of storage space
# https://h3geo.org/docs/core-library/restable
# Resolution 7 is ~2,000m across, 9 is ~320m across, 11 is ~45m (in YT Albers)
min_resolution = 0
max_resolution = 7

# Output files are {prefix}_{resolution}: Hex_3, Hex_4, ...
out_name_prefix = "Hex"

geographic_coordsys = "EPSG:4617"  # e.g. WGS84, NAD83(CSRS)
output_projection = "EPSG:3579"  # placeholder, not currently used
# --------------------------------------------

projectPath = os.path.dirname(QgsProject.instance().fileName())
geo_csrs = QgsCoordinateReferenceSystem(geographic_coordsys)
out_csrs = QgsCoordinateReferenceSystem(output_projection)

dataPath = os.path.abspath(os.path.join(projectPath, "data"))  # use abspath and remove trailing slash

try:
    if not os.path.exists(dataPath):
        os.makedirs(dataPath, exist_ok=True)  # use makedirs instead of mkdir
except PermissionError:
    # If we can't create in project directory, fall back to temp
    dataPath = os.path.abspath(os.path.join(os.environ["TEMP"], "data"))
    os.makedirs(dataPath, exist_ok=True)

#instead of chooser, just use active layer, and selected features within that layer
mylayer = iface.activeLayer()
if mylayer.selectedFeatures():
    params = {'INPUT':mylayer, 'OUTPUT':'memory:sel'}
    mylayer = processing.run("qgis:saveselectedfeatures", params)["OUTPUT"]
    if debug:
        QgsProject.instance().addMapLayer(mylayer)


def log(item):
    return QgsMessageLog.logMessage(str(item))


def proj_to_geo(in_layer):
    """Project to geographic coordinate system, in memory.
    H3 needs all coordinates in decimal degrees"""
    params = {
        "INPUT": mylayer,
        "TARGET_CRS": geographic_coordsys,
        "OUTPUT": "memory:dd_",
    }
    geo_lyr = processing.run("native:reprojectlayer", params)["OUTPUT"]
    if debug:
        QgsProject.instance().addMapLayer(geo_lyr)
    return geo_lyr


def poly_from_extent(layer):
    """Return polygon as coordinate list from layer's extent
    Ex:
        [(-142.0, 74.0), (-115.0, 74.0), (-115.0, 54.0), (-142.0, 54.0)]

    Adapted from
    https://gis.stackexchange.com/questions/245811/getting-layer-extent-in-pyqgis
    """
    ext = layer.extent()
    xmin = ext.xMinimum()
    xmax = ext.xMaximum()
    ymin = ext.yMinimum()
    ymax = ext.yMaximum()
    return [(xmin, ymax), (xmax, ymax), (xmax, ymin), (xmin, ymin)]


def hexes_within_layer_extent(layer, level):
    """Return list of HexID within layer's extent
    In: qgis layer object, hex resolution level (0-15)
    Out: ['8412023ffffffff', '84029d5ffffffff', '8413a93ffffffff']
    """
    ext_poly = poly_from_extent(layer)
    # Convert to format expected by h3: [[lat1, lng1], [lat2, lng2], ...]
    polygon = [[p[1], p[0]] for p in ext_poly]  # swap to lat,lng order
    hex_ids = set()
    
    # Get the bounding box and create a grid of points
    min_lat = min(p[1] for p in ext_poly)
    max_lat = max(p[1] for p in ext_poly)
    min_lng = min(p[0] for p in ext_poly)
    max_lng = max(p[0] for p in ext_poly)
    
    # Calculate step size based on resolution level (rough approximation)
    step = max(0.1, (max_lat - min_lat) / 100)  # adjust step size based on extent
    
    # Sample points within the bounding box
    lat = min_lat
    while lat <= max_lat:
        lng = min_lng
        while lng <= max_lng:
            hex_ids.add(h3.latlng_to_cell(lat, lng, level))
            lng += step
        lat += step
    
    log(f"Hex IDs within extent poly: {str(len(hex_ids))}")
    return hex_ids


geo_layer = proj_to_geo(mylayer)


# For each resolution level fetch geometry of each hex feature and write to shapefile with id
for res in range(min_resolution, max_resolution + 1):
    log(f"Resolution: {res}")
    
    # Create fields for the layer
    fields = QgsFields()
    field = QgsField()
    field.setName("h3_index")
    field.setType(QVariant.String)
    fields.append(field)
    field = QgsField()
    field.setName("resolution")
    field.setType(QVariant.Int)
    fields.append(field)
    
    save_options = QgsVectorFileWriter.SaveVectorOptions()
    save_options.driverName = "ESRI Shapefile"
    save_options.fileEncoding = "UTF-8"
    
    # Create a memory layer first
    uri = f"Polygon?crs={geo_csrs.authid()}"
    memory_layer = QgsVectorLayer(uri, "temp", "memory")
    memory_layer.dataProvider().addAttributes(fields)
    memory_layer.updateFields()
    
    if not memory_layer.isValid():
        log("Error: Invalid memory layer")
        continue
    
    features = []
    for id in set(hexes_within_layer_extent(geo_layer, res)):
        f = QgsFeature(fields)
        f.setAttribute("h3_index", id)
        f.setAttribute("resolution", res)
        
        # Get the hex boundary and create polygon
        boundary = h3.cell_to_boundary(id)
        points = [QgsPointXY(lon, lat) for lat, lon in boundary]
        points.append(points[0])  # close the polygon
        
        f.setGeometry(QgsGeometry.fromPolygonXY([points]))
        features.append(f)
        if debug:
            log(f"Hex: {id} " + str(h3.h3_to_geo_boundary(id)))
    
    # Add features to memory layer
    memory_layer.dataProvider().addFeatures(features)
    
    # Write the memory layer to file
    shpfile = os.path.join(dataPath, f"{out_name_prefix}_{res}.shp")
    error = QgsVectorFileWriter.writeAsVectorFormatV3(
        layer=memory_layer,
        fileName=shpfile,
        transformContext=QgsProject.instance().transformContext(),
        options=save_options
    )
    
    if error[0] != QgsVectorFileWriter.NoError:
        log(f"Error writing vector file: {error[0]}")
        continue
    
    log("Features out: " + str(len(features)))

    # Add the layer to the map with the correct CRS
    layer = QgsVectorLayer(shpfile, f"{out_name_prefix} {res}", "ogr")
    if layer.isValid():
        layer.setCrs(geo_csrs)
        QgsProject.instance().addMapLayer(layer)
        log(f"Added layer {out_name_prefix} {res} to map")
    else:
        log(f"Error: Could not load layer {out_name_prefix} {res}")
