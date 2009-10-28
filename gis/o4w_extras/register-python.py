#!/usr/bin/env python
# -*- coding: latin-1 -*-#
# script to register Python 2.0 or later for use with win32all
# and other extensions that require Python registry settings
#
# written by Joakim Löw for Secret Labs AB / PythonWare
#
# modified by Matt Wilkie for OSGeo4W
#
# Adapted from:
#	http://www.pythonware.com/products/works/articles/regpy20.htm
#	http://effbot.org/zone/python-register.htm
#	http://timgolden.me.uk/python-on-windows/programming-areas/registry.html

import sys
from _winreg import *

# grab some details of python environment running this script
# tweak as necessary
our_version = sys.version[:3]
installpath = sys.prefix

regpath = "SOFTWARE\\Python\\Pythoncore\\"
installkey = "InstallPath"
pythonkey = "PythonPath"
pythonpath = "%s;%s\\Lib\\;%s\\DLLs\\" % (
    installpath, installpath, installpath
)

def get_existing(hkey,regpath):
    ''' retrieve all existing python registrations '''
    #TODO: retrieve install path, to know what program existing reg belong to
    if hkey == 'Current':
        try:
            key = OpenKey(HKEY_CURRENT_USER, regpath)
        except:
            return
    elif hkey == 'All':
        try:
            key = OpenKey(HKEY_LOCAL_MACHINE, regpath)
        except:
            return

    subkeys = []
    i = 0
    while True:
        try:
            subkeys.append (EnumKey (key, i))
            i += 1
            #print subkeys
        except EnvironmentError:
            break
    return subkeys

def RegisterPy(pycorepath, version):
    regpath = pycorepath + version
    print regpath
    try:
        reg = OpenKey(HKEY_LOCAL_MACHINE, regpath)
        regVal = QueryValueEx(reg, installkey)[0]
        print regVal
    except EnvironmentError:
        try:
            reg = CreateKey(HKEY_LOCAL_MACHINE, regpath)
            SetValue(reg, installkey, REG_SZ, installpath)
            SetValue(reg, pythonkey, REG_SZ, pythonpath)
            CloseKey(reg)
        except:
            print "*** Unable to register!"
            return
        print "--- Python", our_version, "is now registered!"
        return
    if (QueryValue(reg, installkey) == installpath and
        QueryValue(reg, pythonkey) == pythonpath):
        CloseKey(reg)
        print "=== Python", our_version, "is already registered!"
        return
    CloseKey(reg)
    print "*** Unable to register!"
    print "*** You probably have another Python installation!"


#---
CurrentUser = get_existing('Current',regpath)
AllUsers = get_existing('All',regpath)
print 'Existing Current User python version(s):\t', CurrentUser
print 'Existing All Users python version(s):\t\t', AllUsers

match = False
try:
    if our_version in CurrentUser:
        match = True
    elif our_version in AllUsers:
        match = True
except:
    if match == False:
        RegisterPy(regpath,our_version)
    else:
        print '\nOur version (%s) already belongs to something else. Skipping...' % (our_version)

#-- the end
