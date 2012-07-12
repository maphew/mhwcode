# Update feature class alias
import arcgisscripting
gp = arcgisscripting.create(9.3) 

gdbTable = 'd:/s/gdb.gdb/wka'
desc = gp.describe(gdbTable)

# Print GDB Table properties
#
print "AliasName:              %s" % desc.AliasName
print "DefaultSubtypeCode:     %s" % desc.DefaultSubtypeCode
print "GlobalIDFieldName:      %s" % desc.GlobalIDFieldName
print "ModelName:              %s" % desc.ModelName
print "RasterFieldName:        %s" % desc.RasterFieldName
print "RelationshipClassNames: %s" % desc.RelationshipClassNames
