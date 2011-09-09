#!/usr/bin/env python
# -*- coding: latin-1 -*-#
# script to register Python 2.0 or later for use with win32all
# and other extensions that require Python registry settings
#
# written by Joakim L�w for Secret Labs AB / PythonWare
#
# modified by Matt Wilkie for OSGeo4W
#
# Adapted from:
#   http://www.pythonware.com/products/works/articles/regpy20.htm
#   http://effbot.org/zone/python-register.htm
#   http://timgolden.me.uk/python-on-windows/programming-areas/registry.html
#
# Known problems:
#   Doesn't detect existing python registrations on 64bit machines,
#   see http://www.mail-archive.com/python-list@python.org/msg266397.html
#
import sys
from _winreg import *

# grab some details of python environment running this script
# tweak as necessary
our_version = sys.version[:3]
our_installpath = sys.prefix

pycore_regpath = "SOFTWARE\\Python\\Pythoncore\\"
installkey = "InstallPath"
pythonkey = "PythonPath"
pythonpath = "%s;%s\\Lib\\;%s\\DLLs\\" % \
        (our_installpath, our_installpath, our_installpath)

def get_existing(hkey, pycore_regpath):
    ''' retrieve existing python registrations '''
    #TODO: retrieve install path, to know what program existing reg belong to
    if hkey == 'Current':
        try:
            key = OpenKey(HKEY_CURRENT_USER, pycore_regpath)
        except WindowsError:
            #print WindowsError()
            return
    elif hkey == 'All':
        try:
            key = OpenKey(HKEY_LOCAL_MACHINE, pycore_regpath)
        except WindowsError:
            #print WindowsError()
            return

    versions = []
    version_path = {}
    i = 0
    while True:
        try:
            versions.append (EnumKey (key, i))
            ver = versions[i]   # e.g. '2.7'
            install_path = QueryValue(key, ver + '\\installpath')   # e.g. HKLM/SOFTWARE/Python/PythonCore/2.7/InstallPath
            version_path[ver] = install_path
            #print install_path
            i += 1
            print ver, version_path[ver]
        except EnvironmentError:
            break
    return versions

def RegisterPy(pycore_regpath, version):
    ''' put this python install into registry '''
    pycore_regpath = pycore_regpath + version
    try:
        reg = OpenKey(HKEY_LOCAL_MACHINE, pycore_regpath)
        regVal = QueryValueEx(reg, installkey)[0]
        print regVal
    except EnvironmentError:
        try:
            reg = CreateKey(HKEY_LOCAL_MACHINE, pycore_regpath)
            SetValue(reg, installkey, REG_SZ, our_installpath)
            SetValue(reg, pythonkey, REG_SZ, pythonpath)
            CloseKey(reg)
        except:
            print "*** Unable to register!"
            return
        print "--- Python %s is now registered to %s!" % (our_version, our_installpath)
        return
    if (QueryValue(reg, installkey) == our_installpath and
        QueryValue(reg, pythonkey) == pythonpath):
        CloseKey(reg)
        print "=== Python %s is already registered!" % (our_version)
        return
    CloseKey(reg)
    print "*** Unable to register!"
    print "*** You probably have another Python installation!"

#---
CurrentUser = get_existing('Current',pycore_regpath)
AllUsers = get_existing('All',pycore_regpath)
print '''
    Existing Current User python version(s):  %s
    Existing All Users python version(s):\t  %s
''' % (CurrentUser, AllUsers)

if CurrentUser:
    match = True if our_version in CurrentUser else False
elif AllUsers:
    match = True if our_version in AllUsers else False
else:
    RegisterPy(pycore_regpath,our_version)

try:
    if match:
        print 'Our version (%s) already registered. Skipping...' % (our_version)
except:
    pass

#-- the end
