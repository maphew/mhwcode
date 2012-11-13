#@+leo-ver=5-thin
#@+node:maphew.20120203103945.1813: * @file xx-calc-trans.py
''' scratchpad file: test out ideas for how to calculate transparency percentage of each ring buffer given approximate start and end values.
'''
ring_width = 1000   # width of each buffer ring
num_rings = 7   # total number of rings to create
darkest = 50    # uppermost layer transparency %
lightest = 80    # lowermost layer transparency %

first_ring = ring_width                 # 1000

#@+others
#@+node:maphew.20120203121800.1759: ** get_transparency_dict
def get_transparency_dict(darkest, lightest, steps):
    '''build dictionary of transparency percentages with specified number of steps
    Returns {0:50, 1:55, 2:60 ...}'''
    transparency_dict = {}
    stepsize = (lightest - darkest) / steps     # percent to lighten/darken each ring
    for e,i in enumerate(range(darkest, lightest, stepsize)):
        # print "Ring #",e+1, "transparency is", i
        transparency_dict[e + 1] = i
    return transparency_dict
#@-others

transparency_dict = get_transparency_dict(darkest, lightest, num_rings)

import arcpy

wspace = 'd:/s/default.gdb'
in_fc = 'FNTT'
out_fc = in_fc + '_buffers'
num_rings = 7
ring_width = 1000
ring_type = 'INSIDE'

sideType = "OUTSIDE_ONLY"
endType = "ROUND"
dissolveType = "LIST"
dissolveFields = "NAME;TYPE"    # attributes we want to keep, adjust as needed 

arcpy.env.workspace = wspace

buffered_fcs = []
for current_ring in range(1, num_rings + 1):
    transparency =  transparency_dict[current_ring]
    width = str(ring_width * current_ring)
    buf_fc = arcpy.ValidateTableName('xxx_' + out_fc + width)
    
    print "...Buffer #{0:2d} width {1} transparency {2}".format(current_ring, width, transparency)
    
    if ring_type == 'INSIDE':
        arcpy.Buffer_analysis(in_fc, buf_fc, '-'+width, sideType, endType, dissolveType, dissolveFields)
    else:
        arcpy.Buffer_analysis(in_fc, buf_fc, width, sideType, endType, dissolveType, dissolveFields)
    
    # store buffer width as attribute value
    arcpy.AddField_management(buf_fc, 'Width', "TEXT", "", "", 16)
    arcpy.CalculateField_management(buf_fc, 'Width', width, "PYTHON")
    
    # store transparency also
    arcpy.AddField_management(buf_fc, 'Transparency', "SHORT")
    arcpy.CalculateField_management(buf_fc, 'Transparency', transparency, "PYTHON")
    
    buffered_fcs.append(buf_fc)
    
# arrange buffers from largest to smallest width
# so the draw order is correct after merging
buffered_fcs.sort()
buffered_fcs.reverse() 

print("...Merging intermediate buffers into {0}".format(out_fc))
arcpy.Merge_management(buffered_fcs, out_fc)

# remove temporary intermediate files
print("...Removing intermediate files")
for fc in arcpy.ListFeatureClasses('xxx_*'):
    arcpy.Delete_management(fc)
#@-leo
