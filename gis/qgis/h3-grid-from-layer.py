"""Generate an h3 index grid from the extents of input layer.
In Qgis:
    Processing Toolbox >> Open existing script >> {select this file}
        >> Select template extent layer in table of contents
            >> optionally select specific features to get extent from
        >> Edit the variables below (particularly min/max)
        >> Run

Adapted from https://github.com/ThomasG77/30DayMapChallenge/blob/master/day4_hexagons/data/h3-processing.py
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
max_resolution = 9

# Output files are {prefix}_{resolution}: Hex_3, Hex_4, ...
out_name_prefix = "Hex"

geographic_coordsys = "EPSG:4617"  # e.g. WGS84, NAD83(CSRS)
output_projection = "EPSG:3579"  # placeholder, not currently used
# --------------------------------------------

projectPath = os.path.dirname(QgsProject.instance().fileName())
geo_csrs = QgsCoordinateReferenceSystem(geographic_coordsys)
out_csrs = QgsCoordinateReferenceSystem(output_projection)

dataPath = os.path.join(projectPath, "data/")
if not os.path.exists(dataPath):
    os.mkdir(dataPath)

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
    hex_ids = set(h3.polyfill_polygon(ext_poly, res=level, lnglat_order=True))
    log(f"Hex IDs within extent poly: {str(len(hex_ids))}")
    return hex_ids


geo_layer = proj_to_geo(mylayer)


# For each resolution level fetch geometry of each hex feature and write to shapefile with id
for res in range(min_resolution, max_resolution + 1):
    log("Resolution: {res}")
    fields = QgsFields()
    fields.append(QgsField("id", QVariant.String))
    shpfile = os.path.join(dataPath, f"{out_name_prefix}_{res}.shp")
    writer = QgsVectorFileWriter(
        shpfile, "UTF8", fields, QgsWkbTypes.Polygon, driverName="ESRI Shapefile"
    )
    features = []
    for id in set(hexes_within_layer_extent(geo_layer, res)):
        f = QgsFeature()
        f.setGeometry(
            QgsGeometry.fromPolygonXY(
                [
                    # note reversing back to X,Y
                    [QgsPointXY(c[1], c[0]) for c in h3.h3_to_geo_boundary(id)]
                ]
            )
        )
        f.setAttributes([id])
        if debug:
            log(f"Hex: {id} " + str(h3.h3_to_geo_boundary(id)))
        features.append(f)
    writer.addFeatures(features)
    del writer
    log("Features out: " + str(len(features)))

    processing.run("qgis:definecurrentprojection", {"INPUT": shpfile, "CRS": geo_csrs})

    layer = QgsVectorLayer(shpfile, f"{out_name_prefix} {res}", "ogr")
    QgsProject.instance().addMapLayer(layer)
