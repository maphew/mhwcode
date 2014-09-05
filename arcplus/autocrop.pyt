#
# Courtesy of Luke Pinner, http://gis.stackexchange.com/a/55179/108
#
import arcpy

class Toolbox(object):
    def __init__(self):
        """Define the toolbox (the name of the toolbox is the name of the
        .pyt file)."""
        self.label = "Raster Toolbox"
        self.alias = ""

        # List of tool classes associated with this toolbox
        self.tools = [ClipNoData]


class ClipNoData(object):
    def __init__(self):
        """Clip raster extent to the data that have values"""
        self.label = "Clip NoData"
        self.description = "Clip raster extent to the data that have values. "
        self.description += "Method by Bill Huber - http://gis.stackexchange.com/a/55150/2856"

        self.canRunInBackground = True

    def getParameterInfo(self):
        """Define parameter definitions"""
        params = []

        # First parameter
        params+=[arcpy.Parameter(
            displayName="Input Raster",
            name="in_raster",
            datatype='GPRasterLayer',
            parameterType="Required",
            direction="Input")
        ]

        # Second parameter
        params+=[arcpy.Parameter(
            displayName="Output Raster",
            name="out_raster",
            datatype="DERasterDataset",
            parameterType="Required",
            direction="Output")
        ]

        return params

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return arcpy.CheckExtension('spatial')==u'Available'

    def execute(self, parameters, messages):
        """See http://gis.stackexchange.com/a/55150/2856
           ##Code comments paraphrased from @whubers GIS StackExchange answer
        """
        try:
            #Setup
            arcpy.CheckOutExtension('spatial')
            from arcpy.sa import *
            in_raster = parameters[0].valueAsText
            out_raster = parameters[1].valueAsText

            dsc=arcpy.Describe(in_raster)
            xmin=dsc.extent.XMin
            ymin=dsc.extent.YMin
            mx=dsc.meanCellWidth
            my=dsc.meanCellHeight
            arcpy.env.extent=in_raster
            arcpy.env.cellSize=in_raster
            arcpy.AddMessage(out_raster)

            ## 1. Convert the grid into a single zone by equating it with itself
            arcpy.AddMessage(r'1. Convert the grid into a single zone by equating it with itself...')
            zones = Raster(in_raster) == Raster(in_raster)

            ## 2. Create a column index grid by flow-accumulating a constant grid
            ##    with value 1. (The indexes will start with 0.) Multiply this by
            ##    the cellsize and add the x-coordinate of the origin to obtain
            ##    an x-coordinate grid.
            arcpy.AddMessage(r'Create a constant grid...')
            const = CreateConstantRaster(1)

            arcpy.AddMessage(r'2. Create an x-coordinate grid...')
            xmap = (FlowAccumulation(const)) * mx + xmin

            ## 3. Similarly, create a y-coordinate grid by flow-accumulating a
            ##    constant grid with value 64.
            arcpy.AddMessage(r'3. Create a y-coordinate grid...')
            ymap = (FlowAccumulation(const * 64)) * my + ymin

            ## 4. Use the zone grid from step (1) to compute the zonal min and
            ##    max of "X" and "Y"
            arcpy.AddMessage(r'4. Use the zone grid from step (1) to compute the zonal min and max of "X" and "Y"...')

            xminmax=ZonalStatisticsAsTable(zones, "value", xmap,r"IN_MEMORY\xrange", "NODATA", "MIN_MAX")
            xmin,xmax=arcpy.da.SearchCursor(r"IN_MEMORY\xrange", ["MIN","MAX"]).next()

            yminmax=ZonalStatisticsAsTable(zones, "value", ymap,r"IN_MEMORY\yrange", "NODATA", "MIN_MAX")
            ymin,ymax=arcpy.da.SearchCursor(r"IN_MEMORY\yrange", ["MIN","MAX"]).next()

            arcpy.Delete_management(r"IN_MEMORY\xrange")
            arcpy.Delete_management(r"IN_MEMORY\yrange")

            # Write out the reduced raster
            arcpy.env.extent = arcpy.Extent(xmin,ymin,xmax+mx,ymax+my)
            output = Raster(in_raster) * 1
            output.save(out_raster)

        except:raise
        finally:arcpy.CheckInExtension('spatial')
