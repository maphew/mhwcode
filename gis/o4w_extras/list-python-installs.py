#http://mail.python.org/pipermail/python-list/2006-January/001313.html

from _winreg import *

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
    return L

def function_in_search_of_a_name():
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
            key = OpenKey(python_key, version_name)
            modification_date = QueryInfoKey(key)[2]
            install_path = QueryValue(key, 'installpath')
            L.append((modification_date, version_name, install_path))
    return L

function_in_search_of_a_name()
