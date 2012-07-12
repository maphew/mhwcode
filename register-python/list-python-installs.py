#@+leo-ver=5-thin
#@+node:maphew.20110908163305.1246: * @file list-python-installs.py
#@@language python
#@@tabwidth -4
#@+others
#@+node:maphew.20110919151420.1854: ** imports
#@verbatim
#@url http://mail.python.org/pipermail/python-list/2006-January/001313.html

from _winreg import *

#@+node:maphew.20110919151420.1855: ** get_subkey_names
def get_subkey_names(reg_key):
    index = 0
    L = []
    while True:
        try:
            name = EnumKey(reg_key, index)
        except EnvironmentError:
            break
        index += 1
        L.append(name)
    
    print '\nget_subkey_names returning: %s\n' % (L)
    
    return L

#@+node:maphew.20110919151420.1856: ** list_keys
def list_keys():
    """
    Return a list with info about installed versions of Python.

    Each version in the list is represented as a tuple with 3 items:

    0   A long integer giving when the key for this version was last
          modified as 100's of nanoseconds since Jan 1, 1600.
    1   A string with major and minor version number e.g '2.4'.
    2   A string of the absolute path to the installation directory.
    """
    python_path = r'software\python\pythoncore'
    L = []
    for reg_hive in (HKEY_LOCAL_MACHINE,
                      HKEY_CURRENT_USER):
        try:
            python_key = OpenKey(reg_hive, python_path)
        except EnvironmentError:
            continue
        for version_name in get_subkey_names(python_key):
            
            print 'version_name:', version_name
            
            key = OpenKey(python_key, version_name)
            modification_date = QueryInfoKey(key)[2]
            
            print key, modification_date
            
            install_path = QueryValue(key, version_name + '\\installpath')
            # on Win7x64-pro fails with "WindowsError: [Error 2] The system cannot find the file specified"
            # because should be opening wow6432 instead??
            # to read: @url http://docs.python.org/library/_winreg.html#bit-specific
            print install_path
            
            L.append((modification_date, version_name, install_path))
    return L

#@-others
list_keys()
#@-leo
