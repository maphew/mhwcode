#@+leo-ver=5-thin
#@+node:maphew.20120201131727.1848: * @file multi-ring-buffer.py
''' multi-ring-buffer.py: Create multiple ring buffers, keeping named attributes of parent feature class.

Process:
    - create inside only buffer for each of the specifed buffer widths
    - store buffer width used as an attribute
    - merge all buffers into a single feature class, ensuring largest width first so narrower ones are drawn on top

Requires Arcgis 10, Arcinfo license level.

(c) 2012 Environment Yukon, matt.wilkie@gov.yk.ca
Licensed under the MIT license: http://www.opensource.org/licenses/MIT

Also see http://gis.stackexchange.com/questions/19505/multiple-ring-buffer-with-attributes
'''

import arcpy
from arcpy import env

in_fc = r'R:\v5\ENV_1000k.gdb\admin_other\FNTT' # features to buffer
out_fc = 'FNTT_ringbuffers'                                 # finished result
distances = ['-1000','-3000','-5000']                      # buffer widths, add as desired
wspace = 'D:/s/default.gdb/'

env.workspace = wspace

sideType = "OUTSIDE_ONLY"
endType = "ROUND"
dissolveType = "LIST"
dissolveFields = "NAME;TYPE"    # attributes we want to keep, adjust as needed 

buffered_fcs = []
for distance in distances:
    buf_fc = arcpy.ValidateTableName('xxx_' + out_fc + distance)
    
    arcpy.Buffer_analysis(in_fc, buf_fc, distance, sideType, endType, dissolveType, dissolveFields)
    
    # store buffer width as attribute value
    arcpy.AddField_management(buf_fc, 'Width', "TEXT", "", "", 16)
    arcpy.CalculateField_management(buf_fc, 'Width', distance, "PYTHON")
    
    buffered_fcs.append(buf_fc)

# arrange buffers from largest to smallest width
# so the draw order is correct after merging
buffered_fcs.sort()
buffered_fcs.reverse() 

arcpy.Merge_management(buffered_fcs, out_fc)

## remove temporary intermediate files
#for fc in arcpy.ListFeatureClasses('xxx_*')
#    arcpy.Delete_management(fc)
#@-leo
