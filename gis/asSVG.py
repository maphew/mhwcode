#############################################################################
#
# $Id: asSVG.py 57 2008-11-27 13:27:04Z klaus $
#
# Copyright (C) 2008, Klaus Foerster <klaus.foerster@svg.cc>
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
#############################################################################


import os, re, sys
import locale

from cgi import escape

GP = None
try:
    # no PythonWin needed any more since of ArcGIS 9.2
    import arcgisscripting
    GP = arcgisscripting.create()
except:
    import win32com.client
    GP = win32com.client.Dispatch("esriGeoprocessing.GPDispatch.1")

# set override flag
GP.OverwriteOutput = 1

from math import sqrt

SVG_DEFAULT_COLOR = "#CCC"
SVG_DEFAULT_TEXT_COLOR = "#000"
SVG_DEFAULT_STROKE = "#000"
SVG_DEFAULT_STROKE_WIDTH = 0.002    # stroke-width in percentage of svg viewport
SVG_DEFAULT_CIRCLE_RADIUS = 0.01    # circle radius in percentage of svg viewport
SVG_DEFAULT_FONT_SIZE = 0.04        # font-size in in percentage of svg viewport

########################
#
# SVG export class
#
########################

class SVGLib:
    def __init__(self,gp=None,argv=None):
        # set locale, what a mess in ArcGIS :(
        locale.setlocale(locale.LC_ALL, "english")

        """ set globals """
        self.prefix = "assvg"
        self.namespace = "http://svg.cc/ns/assvg"
        self.missingval = "#"
        self.absolute = 0
        self.paths = []
        self.points = []
        self.stylesheet = {}

        # initialize geoprocessing
        self.gp = gp

        # define layer, precision, classfield and datafields
        self.script = argv[0]
        self.layer = argv[1]
        self.relative = argv[2]
        self.layer_type =  self._setLayerType(self.relative)
        self.precision = self._setPrecision(argv[3])
        self.classfield = self._asList(argv[4])
        self.datafields = self._asList(argv[5])
        self.outputfile = argv[6]

        """ parse extent of layer and set viewBox for SVG accordingly"""
        bbox = map(self._round,self.gp.describe(self.layer).Extent.split(" "))
        self.extent = [ bbox[0],bbox[3]*-1,bbox[2]-bbox[0],bbox[3]-bbox[1] ]

        # initialize colorsystem and define colors
        ##self.libPath = "%s" % re.sub("\\\[^\\\]+$","",argv[0])
        self.libPath = os.path.dirname(os.path.realpath(__file__))
            #fix Windows `[Errno 2] No such file or directory: 'asSVG.py/Tango-Palette.gpl'`
        self.colors = SVGColor(gp,self.libPath)
        
    ########################
    #
    # private methods
    #
    ########################

    def _setPrecision(self,value):
        """ return precision as integer or None """
        try:
            return int(value)
        except:
            return None

    def _setLayerType(self,relative):
        """ set abbreviation for layer-type """
        ltype = self.gp.describe(self.layer).ShapeType
        if ltype=='Polygon':
            return 'ply'
        elif ltype=='Polyline':
            return 'lin'
        elif ltype=='Point':
            if relative == 'false':
                return 'txt'
            else:
                return 'pnt'
        else:
            return 'default'
            
    def _asList(self,value):
        """ return list-presentation of value, separator=';' """
        if re.search(";",value):
            return str(value).split(";")
        else:
            if value == self.missingval:
                return [ ]
            else:
                return [value]

    def _asString(self,value):
        """ return value as string or none """
        if not value:
            return None
        elif str(type(value)) == "<type 'unicode'>":
            return str(value.encode('utf-8'))
        else:
            return str(value)

    def _round(self,value):
        """ round coordinates according to defined precision """
        value = re.sub(",",".",str(value))
        if self.precision == None:
            value = float("%s" % value)
        elif self.precision == 0:
            value = int(round(float(value),self.precision))
        else:
            value = round(float(value),self.precision)

        return value

    def _inPercent(self,value):
        """ compute percentages for attributes like stroke-width, r, ... 
            follows SVG 1.1 spec http://www.w3.org/TR/SVG/coords.html#Units"""
        if self.extent:
            return self._round(value*(sqrt((self.extent[2]**2)+(self.extent[3]**2))/sqrt(2)))
        return value

    def _asSaveAttrName(self,value):
        """ strip invalid chars from identifiers """
        value = re.sub("[^A-Za-z0-9-]","-",value)
        return value or "default"

    def _makePath(self,row,coords):
        """ create polygon or polyline in SVG notation"""
        code = []
        code.append("<path ")
        code.append("""class="%s" """ % (self._getClass(row)))            
        code.append("%s " % self._getData(row))            
        code.append("""d="%s" />""" % (coords))
        return "".join(code)

    def _makePoint(self,row,cx,cy):
        """ create circle in SVG notation"""
        code = []
        code.append("<circle ")
        code.append("""class="%s" """ % (self._getClass(row)))            
        code.append("%s " % self._getData(row))            
        code.append("""cx="%s" cy="%s" r="%s" />""" % (cx,cy,self._inPercent(SVG_DEFAULT_CIRCLE_RADIUS)))
        return "".join(code)
        
    def _makeText(self,row,cx,cy):
        """ create text in SVG notation"""
        code = []
        code.append("<text ")
        code.append("""class="%s" """ % (self._getClass(row)))            
        code.append("""x="%s" y="%s">""" % (cx,cy))
        code.append("%s" % self._getTextData(row))            
        code.append("</text>")
        return "".join(code)

    def _getClass(self,row):
        """ extract class if needed """
        if len(self.classfield) == 0:
            return "%sdefault" % self.layer_type

        cls = "%s%s" % (self.layer_type,self._asString(row.getValue(self.classfield[0])))
        cls = self._asSaveAttrName(cls)
        if not self.stylesheet.has_key(cls):
            (color,cname) = self.colors.getNextColor()
            if self.layer_type == 'ply':
                self.stylesheet[cls] = """ .%s {stroke:none;fill:%s; } /* %s */""" % (cls,color,cname)
            elif self.layer_type == 'lin':
                self.stylesheet[cls] = """ .%s {stroke:%s;fill:none;stroke-width:%s; } /* %s */""" % (cls,color,self._inPercent(SVG_DEFAULT_STROKE_WIDTH),cname)
            elif self.layer_type == 'pnt':
                self.stylesheet[cls] = """ .%s {stroke:%s;fill:%s;stroke-width:%s; } /* %s */""" % (cls,SVG_DEFAULT_STROKE,color,self._inPercent(SVG_DEFAULT_STROKE_WIDTH),cname)
            elif self.layer_type == 'txt':
                self.stylesheet[cls] = """ .%s {fill:%s;font-size:%spx; } /* %s */""" % (cls,color,self._inPercent(SVG_DEFAULT_FONT_SIZE),cname)
            else:
                self.gp.AddError("Unknown layer-type found.")
        return cls

    def _getData(self,row):
        """ fill data attributes if needed """
        attribs = []
        for field in self.datafields:
            try:
                if row.getValue(field):
                    attribs.append("""%s:%s="%s" """ % (self.prefix,self._asSaveAttrName(field.lower()),escape(self._asString(row.getValue(field)),1)))
            except:
                continue
        return "".join(attribs)

    def _getTextData(self,row):
        """ collect text for labels from data attributes if needed """
        labels = []        
        for field in self.datafields:
            try:
                if row.getValue(field):
                    labels.append("%s" % escape(self._asString(row.getValue(field)),1))
            except:
                continue
        return ", ".join(labels)

    def _getStyleSheet(self):
        """ return text-presentation of collected stylesheet"""
        sheet = []
        for cls in self.stylesheet.keys():
            sheet.append(self.stylesheet[cls])
        return "\n".join(sheet)

    ########################
    #
    # main geometry parser
    #
    ########################
    
    def parseCoords(self):
        self.gp.AddMessage("Processing coords of %s (%s) ..." % (self.layer,self.layer_type))

        if self.layer_type == "ply" or self.layer_type == "lin" :
            rows = self.gp.SearchCursor(self.layer)
            row = rows.Next()

            while row:
                i = 0
                coords = ""
                while i < row.shape.PartCount:
                    lastX = None
                    lastY = None
                    coords += "M "

                    j = 0
                    part = row.shape.GetPart(i)
                    part.Reset()
                    pnt = part.Next()

                    while pnt:
                        if self.relative == 'false':
                            coords += "%s %s " % (self._round(pnt.x),self._round(pnt.y*-1))
                        else:
                            if lastX and lastY:
                                relX = pnt.x - lastX
                                relY = (pnt.y*-1) - lastY
                                lastX = pnt.x
                                lastY = pnt.y*-1
                                coords += "%s %s " % (self._round(relX),self._round(relY))
                            else:
                                lastX = pnt.x
                                lastY = pnt.y*-1
                                coords += "%s %s l " % (self._round(lastX),self._round(lastY))

                        pnt = part.Next()
                        if not pnt:
                            pnt = part.Next()
                            if pnt:
                                j = j + 1
                                coords += "M "
                                lastX = None
                                lastY = None
                    i = i + 1

                self.paths.append(self._makePath(row,coords))
                row = rows.Next()

        else:
            rows = self.gp.SearchCursor(self.layer)
            row = rows.Next()
            while row:
                if row.shape.IsMultipart == "TRUE":
                    i = 0
                    while i < row.shape.PartCount:
                        part = row.shape.GetPart(i)
                        part.Reset()
                        pnt = part.Next()
                        if self.layer_type == 'txt':
                            self.points.append(self._makeText(row,self._round(pnt.x),self._round(pnt.y)*-1))
                        else:
                            self.points.append(self._makePoint(row,self._round(pnt.x),self._round(pnt.y)*-1))
                        i += 1
                else:
                    pnt = row.shape.GetPart(0)
                    if self.layer_type == 'txt':
                        self.points.append(self._makeText(row,self._round(pnt.x),self._round(pnt.y)*-1))                    
                    else:
                        self.points.append(self._makePoint(row,self._round(pnt.x),self._round(pnt.y)*-1))

                row = rows.Next()


    ########################
    #
    # print out result to file
    #
    ########################
    
    def writeFile(self):
        """ return a simple SVG presentation of results """
        code = """<?xml version="1.0" encoding="UTF-8" ?>
<svg
 version="1.1"
 baseProfile="full"
 xmlns="http://www.w3.org/2000/svg"
 xmlns:xlink="http://www.w3.org/1999/xlink"
 xmlns:%s="%s"
 viewBox="%s %s %s %s"
>
<style type="text/css"><![CDATA[
 .lindefault { fill:none;stroke:%s;stroke-width:%s; }
 .plydefault { fill:%s;stroke:none; }
 .pntdefault { fill:%s;stroke:%s;stroke-width:%s; }
 .txtdefault { fill:%s;stroke:none;font-size:%spx; }
%s
]]></style>
%s
%s
</svg>
""" % (
        self.prefix,self.namespace,
        self.extent[0],self.extent[1],self.extent[2],self.extent[3],
        SVG_DEFAULT_COLOR,self._inPercent(SVG_DEFAULT_STROKE_WIDTH),
        SVG_DEFAULT_COLOR,
        SVG_DEFAULT_COLOR,SVG_DEFAULT_STROKE,self._inPercent(SVG_DEFAULT_STROKE_WIDTH),
        SVG_DEFAULT_TEXT_COLOR,self._inPercent(SVG_DEFAULT_FONT_SIZE),
        self._getStyleSheet(),
        "\n".join(self.points),
        "\n".join(self.paths)
       )
        
        out = open(self.outputfile,"w")
        out.write(code)
        out.close()
        self.gp.AddWarning("Created %s." % self.outputfile)


class SVGColor:
    def __init__(self,gp,libPath):
        """ initialize new colormap """
        self.gp = gp
        self.libPath = libPath
        self.sequence = 0
        self.palette = []
        self._loadColorMap('Tango-Palette.gpl')

    def _loadColorMap(self,gpl):
        """ load colormap and define colors """
        f = open("%s/%s" % (self.libPath,gpl))
        for line in f.readlines():
            line = re.sub(" +"," ",line.rstrip().lstrip())
            line = re.sub("\t+"," ",line)
            row = line.split(" ")
            if len(row) == 5 and re.match("^[0-9]+$",row[0]):
                rgb = "rgb(%s,%s,%s)" % (row[0],row[1],row[2])
                txt = " ".join(row[3:])
                self.palette.append([rgb,txt])
        f.close()

    def getNextColor(self):
        """ return next color of palette, rewind at end of palette """
        if self.sequence == len(self.palette)-1:
            self.sequence = 0
        self.sequence += 1
        return self.palette[self.sequence-1]


if __name__ == "__main__":
    """This tool converts ArcGIS layers to simple SVG notation."""
    try:
        # process layer or shape
        svg = SVGLib(GP,sys.argv)
        svg.parseCoords()
        svg.writeFile()

    except Exception, ErrorDesc:
        # Except block if the tool could not run at all.
        GP.AddError(str(ErrorDesc))
        print str(ErrorDesc)

