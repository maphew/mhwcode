#!/usr/bin/env python
# -*- coding: latin-1 -*-#
# script to register Python 2.0 or later for use with win32all
# and other extensions that require Python registry settings
#
# written by Joakim L�w for Secret Labs AB / PythonWare
#
# source:
# http://www.pythonware.com/products/works/articles/regpy20.htm

import sys

from _winreg import *

# tweak as necessary
version = sys.version[:3]
installpath = sys.prefix

regpath = "SOFTWARE\\Python\\Pythoncore\\%s\\" % (version)
installkey = "InstallPath"
pythonkey = "PythonPath"
pythonpath = "%s;%s\\Lib\\;%s\\DLLs\\" % (
    installpath, installpath, installpath
)

# http://sebsauvage.net/python/snyppets/#registry
key = OpenKey(HKEY_CURRENT_USER, regpath, 0, KEY_READ)
(value, valuetype) = QueryValueEx(key, installkey)
print value
print valuetype


def RegisterPy():
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
        print "--- Python", version, "is now registered!"
        return
    if (QueryValue(reg, installkey) == installpath and
        QueryValue(reg, pythonkey) == pythonpath):
        CloseKey(reg)
        print "=== Python", version, "is already registered!"
        return
    CloseKey(reg)
    print "*** Unable to register!"
    print "*** You probably have another Python installation!"

if __name__ == "__main__":
    RegisterPy()

