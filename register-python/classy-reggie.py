#!/usr/bin/env python
# courtesy of Winston Ewert
# http://codereview.stackexchange.com/questions/5217/all-tangled-up-in-if-and-elif-and-try/5218#5218

import sys
#from _winreg import *
import _winreg
import argparse, sys
import os.path

PYTHON_VERSION = "%d.%d" % sys.version_info[0:2]

# the registry key paths we'll be looking at & using
PYCORE_REGISTRY_PATH = ("SOFTWARE","Python","Pythoncore")
INSTALL_KEY = "InstallPath"
PYTHON_KEY = "PythonPath"
PYTHONPATH = ";".join( os.path.join(sys.prefix, sub) for sub in ["", "Lib", "DLLs"])

class RegisteryKeyNotFound(Exception):
    pass

class RegisteryKey(object):
    def __init__(self, key):
        self._key = key

    def _path_from(self, segments):
        if not isinstance(segments, tuple):
            segments = (segments,)

        return "\\".join(segments)

    def __getitem__(self, segments):
        try:
            subkey = _winreg.OpenKey(self._key, self._path_from(segments))
        except WindowsError:
            # should really check the error
            # to make sure that key not found is the real problem
            raise RegisteryKeyNotFound(path)
        return RegisteryKey(subkey)

    def get_or_create(self, segments):
        subkey = _winreg.CreateKey(self._key, self._path_from(segments))
        return RegisteryKey(subkey)


    def value(self, segments):
        return _winreg.QueryValue(self._key, self._path_from(segments))

    def delete(self, segments):
        _winreg.DeleteKey(self._key, self._path_from(segments))

    def set_value(self, segments, value):
        _winreg.SetValue(self._key, self._path_from(segments), REG_SZ, value)

    def __iter__(self):
        index = 0
        while True:
            try:
                yield RegisteryKey(EnumKey(key, index))
            except WindowsError:
                # add check to make sure correct here was gotten
                break
            else:
                index += 1

    def __del__(self):
        _winreg.CloseKey(self._key)

HIVE_LOCAL_MACHINE = RegisteryKey('HKEY_LOCAL_MACHINE')
HIVE_CURRENT_USER = RegisteryKey('HKEY_CURRENT_USER')

def get_existing(hive):
    ''' retrieve existing python registrations '''

    try:
        key = hive[PYCORE_REGISTRY_PATH]
    except RegisteryKeyNotFound:
        return {}

    versions = {}
    for version in key:
        versions[version] = version.value(INSTALL_KEY)                           # e.g. {'2.7' = 'C:\\Python27'}

    return versions

def register_python(version):
    ''' put this python install into registry '''
    try:
        reg = HIVE_LOCAL_MACHINE[PYCORE_REGISTRY_PATH][version]
    except RegisteryKeyNotFound:
        reg = HIVE_LOCAL_MACHINE.get_or_create(PYCORE_REGISTRY_PATH).get_or_create(version)
        reg.set_value(INSTALL_KEY, sys.prefix)
        reg.set_value(PYTHON_KEY, PYTHONPATH)
        print "--- Python %s is now registered to %s!" % (PYTHON_VERSION, sys.prefix)
    else:
        print reg.value(INSTALL_KEY)

    if reg.value(INSTALL_KEY) == sys.prefix and reg.value(PYTHON_KEY) == PYTHONPATH:
        print "=== Python %s is already registered!" % (PYTHON_VERSION)
    else:
        print "*** Unable to register!"
        print "*** You probably have another Python installation!"

def deregister_python(version):
    ''' remove this python install from registry '''
    reg = HIVE_LOCAL_MACHINE[PYCORE_REGISTRY_PATH][version]
    install_path = reg.value(INSTALL_KEY)
    if install_path == sys.prefix:
        print '\nexisting python matches ours, removing...\n'
        for subkey in ['InstallPath', 'PythonPath']:
            reg.delete(subkey)
        reg.delete()
        print "--- Python %s, %s is now removed!" % (PYTHON_VERSION, sys.prefix)

def install(installed_versions):
    ''' see if any existing registrations match our python version, and if not, register ours '''

    print '\n...installing'

    if PYTHON_VERSION in installed_versions:
        print '\nOur version (%s) already registered to "%s", skipping...' % (PYTHON_VERSION, installed_versions[PYTHON_VERSION])
    else:
        print '\nPutting python from environment into registry...\n'
        register_python()

def remove(installed_versions):
    ''' see if any existing registrations match our python version and register ours if not '''
    #print args
    if PYTHON_VERSION in installed_versions:
        deregister_python()
    else:
        print '\nOur version (%s) not registered, skipping...' % (PYTHON_VERSION)



# @url http://stackoverflow.com/questions/4042452/display-help-message-with-python-argparse-when-script-is-called-without-any-argum
# display the usage message when it is called with no arguments
class MyParser(argparse.ArgumentParser):
    def error(self, message):
        sys.stderr.write('error: %s\n' % message)
        self.print_help()
        sys.exit(2)



def main():
    parser=MyParser()
    parser.add_argument('action', help='one of "install" or "remove" ')
    args = parser.parse_args()

    current_user_versions = get_existing(HIVE_CURRENT_USER)
    local_machine_versions = get_existing(HIVE_LOCAL_MACHINE)

    print '\nFound in Current User:'
    for key, value in current_user_versions.items():
        print "\t%s - %s" % (key, value)
    print '\nFound in All Users:'
    for key, value in local_machine_version.items():
        print "\t%s - %s" % (key, value)

    all_versions = {}
    all_versions.update(current_user_versions)
    all_versions.update(local_machine_versions)


    if args.action == 'install':
        install(all_versions)
    elif args.action == 'remove':
        remove(all_versions)
    else:
        print '\nInvalid action specified. I only understand "install" and "remove". '

if __name__ == '__main__':
    main()

