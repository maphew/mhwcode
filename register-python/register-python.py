#!/usr/bin/env python
# -*- coding: latin-1 -*-#
#@+leo-ver=5-thin
#@+node:maphew.20120311144705.1358: * @file register-python.py
#@@first
#@@first
#@+<<docstring>>
#@+node:maphew.20110909213512.1219: ** <<docstring>>
""" Install or remove python from current environment into the Windows registry.

When asked to install:

If our python version and installpath is in registry: do nothing.
If our python version and different installpath: do nothing.
If our python is not there, add it.

When asked to remove:

If our python is not there: do nothing
If our python version and different installpath: do nothing.
If our python version and installpath is in registry: remove. 

Original written by Joakim Löw for Secret Labs AB / PythonWare.
Modified by Matt Wilkie for OSGeo4W

Adapted from:
  http://www.pythonware.com/products/works/articles/regpy20.htm
  http://effbot.org/zone/python-register.htm
  http://timgolden.me.uk/python-on-windows/programming-areas/registry.html

Known problems:
  Doesn't detect existing python registrations on 64bit machines,
  see http://www.mail-archive.com/python-list@python.org/msg266397.html
"""
#@verbatim
#@url http://codereview.stackexchange.com/questions/5217/all-tangled-up-in-if-and-elif-and-try
#@-<<docstring>>
#@+<<imports>>
#@+node:maphew.20110908224431.1214: ** <<imports>>
import sys
from _winreg import *

#@-<<imports>>
#@+others
#@+node:maphew.20110914213235.1221: ** parse command line
#@verbatim
#@url http://www.doughellmann.com/PyMOTW/argparse/
import argparse

# @url http://stackoverflow.com/questions/4042452/display-help-message-with-python-argparse-when-script-is-called-without-any-argum
# display the usage message when it is called with no arguments
class MyParser(argparse.ArgumentParser):
    def error(self, message):
        sys.stderr.write('error: %s\n' % message)
        self.print_help()
        sys.exit(2)

# parser=MyParser()
# actions = "list, install, remove"
# parser.add_argument('action', help='one of: %s' % actions)
# args = vars(parser.parse_args())
#@+node:maphew.20110909213512.1220: ** environment & variables
# grab some details of python environment running this script
our_version = sys.version[:3]
our_installpath = sys.prefix

# the registry key paths we'll be looking at & using
pycore_regpath = "SOFTWARE\\Python\\Pythoncore\\"
installkey = "InstallPath"
pythonkey = "PythonPath"

pythonpath = "%s;%s\\Lib\\;%s\\DLLs\\" % \
        (our_installpath, our_installpath, our_installpath)
        
#@+node:maphew.20120311215800.1373: ** functions
#@+node:maphew.20120311215800.1374: *3* usage
def usage():
    prog = sys.argv[0]
    print '''
    Usage: %s [list, install, remove]\n
    
        list    - report existing python installs in registry
        install - attempt to add this python to registry
        remove  - remove this python from registry
        
                  (this python is %s)
    ''' % (prog, our_installpath)
    sys.exit()
        
#@+node:maphew.20110908224431.1215: *3* get_existing
def get_existing(hkey, pycore_regpath):
    ''' Retrieve existing python registrations, 
        returns dict like {'2.7': 'C:\\Python27'} '''

    if hkey == 'Current':
        try:
            key = OpenKey(HKEY_CURRENT_USER, pycore_regpath)
        except WindowsError:
            print WindowsError()
            # raise            
            return
    elif hkey == 'All':
        try:
            key = OpenKey(HKEY_LOCAL_MACHINE, pycore_regpath)
        except WindowsError:
            print WindowsError()
            # raise
            return

    i = 0
    versions = {}
    while True:
        try:
            ver = (EnumKey (key, i))                                      # e.g. '2.7'
            install_path = QueryValue(key, ver + '\\installpath')  # e.g. HKLM\\SOFTWARE\\Python\\PythonCore\\2.7\\InstallPath
            versions[ver] = install_path                                   # e.g. {'2.7' = 'C:\\Python27'}
            i += 1
            # print versions
        except EnvironmentError:
            break
    return versions
#@+node:maphew.20110920221105.1383: *3* report_existing
def report_existing(CurrentUser, AllUsers):
    ''' Display existing python installs in registry '''
    print "Current python installs in registry:"
    if CurrentUser:
        print '\nCurrent User:'
        for key in CurrentUser:
            print "\t%s - %s" % (key, CurrentUser[key])
    if AllUsers:
        print '\nAll Users:'
        for key in AllUsers:
            print "\t%s - %s" % (key, AllUsers[key])
#@+node:maphew.20110908224431.1216: *3* RegisterPy
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

#@+node:maphew.20110920221105.1385: *3* deRegisterPy
def deRegisterPy(pycore_regpath, version):
    ''' remove this python install from registry '''
    pycore_regpath = pycore_regpath + version   # e.g. 'SOFTWARE\Python\Pythoncore\2.7'
    try:
        reg = OpenKey(HKEY_LOCAL_MACHINE, pycore_regpath)
        # installpath = QueryValueEx(reg, installkey)[0] # win64
        installpath = QueryValue(reg, installkey) # win32
        if installpath == our_installpath:
            print 'Confirmed match of version# and install path, removing...\n'
            # print '(%s vs %s)' % (installpath, our_installpath)
            for subkey in ['\\InstallPath', '\\PythonPath']:
                DeleteKey(HKEY_LOCAL_MACHINE, pycore_regpath + subkey)
            DeleteKey(HKEY_LOCAL_MACHINE, pycore_regpath)
            print "--- Python %s, %s is now removed!" % (our_version, our_installpath)
        CloseKey(reg)
    except EnvironmentError:
        print 'EnvironmentError', EnvironmentError()
        raise
        return
    except WindowsError:
        print "Strange, we've hit an exception, perhaps the following will say why:"
        print WindowsError()
        raise
        return
    # except:
        # print 'oops. something else happened'
        # raise
    CloseKey(reg)
    # if (QueryValue(reg, installkey) == our_installpath and
        # QueryValue(reg, pythonkey) == pythonpath):
        # CloseKey(reg)
        # print "=== Python %s is already registered!" % (our_version)
        # return
    # print "*** Unable to de-register!"
    # print "*** You probably have another Python installation!"
#@+node:maphew.20110920221105.1381: *3* do install
def install():
    ''' see if any existing registrations match our python version, and if not, register ours '''
              
    # print args
    # print CurrentUser
    # print AllUsers
    # print our_version
    # print '\n...installing'
    
    match = False
    
    if CurrentUser:
        match = True if our_version in CurrentUser else False
        versions = CurrentUser
        print 'current users', match
    elif AllUsers:
        match = True if our_version in AllUsers else False
        versions = AllUsers
        # print '\nDoes our_version match Allusers version?', match
    
    try:
        if match:
            print '\nOur version (%s) already registered to "%s", skipping...' % (our_version, versions[our_version])
        else:
            print '\nPutting python from environment into registry...\n'
            RegisterPy(pycore_regpath,our_version)
    except:
        raise

#@+node:maphew.20110920221105.1382: *3* do remove
def remove():
    ''' see if any existing registrations match our python version and register ours if not '''
    #print args
    
    match = False
    versions = {}

    if CurrentUser:
        match = True if our_version in CurrentUser else False
        versions = CurrentUser
    elif AllUsers:
        match = True if our_version in AllUsers else False
        versions = AllUsers
    else:
        # print '\nOur version (%s) not registered to "%s", skipping...' % (our_version, versions[our_version])
        print '\nOur version (%s, %s) not registered, skipping...' % (our_version, our_installpath)
    
    try:
        if match:
            print '\nVersion # matches ours, calling deRegisterPy...'
            deRegisterPy(pycore_regpath,our_version)
    except:
        raise
        
#@-others

if len(sys.argv) == 1:
    usage()

# main
CurrentUser = get_existing('Current',pycore_regpath)
AllUsers = get_existing('All',pycore_regpath)
report_existing(CurrentUser, AllUsers)

if len(sys.argv) > 1:
    if sys.argv[1] == 'install':
        install()
    elif sys.argv[1] == 'remove':
        remove()

    
# if args['action']=='install':
    # install()
# elif args['action']=='remove':
    # remove()
# else:
    # print '\nInvalid action specified. I only understand "install" and "remove". '
            
#-- the end
#@-leo
