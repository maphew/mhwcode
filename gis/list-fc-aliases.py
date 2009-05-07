# my first start-to-finish script using Leo Editor
# Displays the names and aliases for all the feature classes in a geodatabases
# (prep work for learning how to import Canvec feature classes from GML, while 
# making use of 
# http://code.google.com/p/maphew/source/browse/trunk/gis/canvec/db-friendly-names.txt)
# Matt Wilkie, begun 2009 May 01
import sys, arcgisscripting
gp = arcgisscripting.create(9.3)
ws_root = sys.argv[1]
gp.workspace = ws_root

name_table = {}

def getDataSets():
    ''' Get feature datasets in current workspace and call listFeatureClassNames on each '''
    fds = gp.ListDatasets()
    for fd in fds:
        print ("\n%s\%s:") % (gp.workspace, fd)
        listFeatureClassNames(fd)
    return

def listFeatureClassNames(path):
    ''' Build table of Feature Class Name <-> Alias Names from FCs in specified path'''
    gp.workspace = path
    fcs = gp.ListFeatureClasses()
    for fc in fcs:
        desc = gp.describe(fc)
        #print '%s \t %s' % (desc.aliasname, desc.name)
        name_table[desc.name] = desc.aliasname
        gp.workspace = ws_root
    return

def reportResult(table):
    ''' Print alias <-> feature class lookup table ''' 
    print '%s -- %50s' % ('Alias', 'Feature Class')
    for name, aliasname in sorted(table.items()):
        print '%s -- %50s' % (aliasname, name)
    return

getDataSets()
listFeatureClassNames(ws_root) # catch feature classes not in Feature Dataset container
reportResult(name_table)
