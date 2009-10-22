#!/usr/bin/env python
# -*- coding: latin-1 -*-#
# script to register Python 2.0 or later for use with win32all
# and other extensions that require Python registry settings
#
# written by Joakim Löw for Secret Labs AB / PythonWare
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

#FIXME: check for HKCU Python before going on to HKLM
#Q: do we register for current user or all users? (HKCU or HKLM?)
#FIXME: handle 64bit machines, http://www.python-forum.org/pythonforum/viewtopic.php?f=15&t=12685

#TODO: http://timgolden.me.uk/python-on-windows/programming-areas/registry.html
regpath = r"software\python\pythoncore"
key = OpenKey(HKEY_CURRENT_USER, regpath)
subkeys = []
i = 0
while True:
    try:
        subkeys.append (EnumKey (key, i))
        i += 1
        print subkeys
    except EnvironmentError:
        break

# http://effbot.org/librarybook/winreg.htm
# this lists values within keys, but skips keys within keys
def ExploreReg():
    explorer = OpenKey(
    HKEY_CURRENT_USER,
    regpath    
    )
    # list values owned by this registry key
    try:
        i = 0
        while 1:
            name, value, type = EnumValue(explorer, i)
            print repr(name),
            i += 1
    except WindowsError:
        print
    #
    #value, type = QueryValueEx(explorer, "Logon User Name")
    #
    #print
    #print "user is", repr(value)
    try:
        i = 0
        while 1:
            name, value, type = EnumKey(regpath, i)
            print repr(name),
            i += 1
    except WindowsError:
        print

ExploreReg()

## http://sebsauvage.net/python/snyppets/#registry
#key = OpenKey(HKEY_CURRENT_USER, 'Software\\Microsoft\\Internet Explorer', 0, KEY_READ)
#key2 = 'Desktop'
#(value, valuetype) = QueryValueEx(key, key2)
#print value
#print valuetype


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
    #RegisterPy()
    pass

