#@+leo-ver=5-thin
#@+node:maphew.20130126213204.1603: * @file apt-skeleton.py
""" the simplest thing that could possibly work, maybe
    yet another attempt at making apt more modular and comprehensible, to me
    this time by breaking the actions into separate files/modules
"""
import os
import sys

root_dir = sys.argv[1]
system = sys.argv[2]

# globals
if not system:
    system = 'OSGEO4W'
else:
    system = sys.argv[2]


def setup(path):
    print 'mkdir %s' % root_dir
    root = OSGEO4W_ROOT
    config = root + '/etc/setup/'
    setup_ini = config + '/setup.ini'
    setup_bak = config + '/setup.bak'
    installed_db = config + '/installed.db'
    installed_db_magic = 'INSTALLED.DB 2\n'


def wrap_up():
    os.putenv(system + '_ROOT', path)

if __name__ == '__main__':
    setup(path)

#@-leo
