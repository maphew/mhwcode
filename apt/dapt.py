#!/usr/bin/env python
'''Yet another dev run at making apt better, and improving my understanding of python.
2014-Sep-27, mhw'''
import os
import sys

import getopt
import glob
import re
import shutil
import string
import urllib
import gzip, tarfile, bz2
import hashlib
import subprocess
import shlex

def get_config():
    '''Configuration values which are used by all functions.
    current form is ugly, hard to read, but works. a simple ini like form is
    better for reading, but I don't know how to code with equal clarity.
    
          root = 'c:/osgeo4w'
          etc_setup = 'c:/osgeo4w/etc/setup'
          setup_ini = 'c:/osgeo4w/etc/setup/setup.ini'
          ...
    '''
    global config
    config = {}
    config['root'] = 'C:/OSGeo4W'
    config['etc_setup'] = config['root'] + '/etc/setup'
    config['setup_ini'] = config['etc_setup'] + '/setup.ini'
    config['setup_bak'] = config['etc_setup'] + '/setup.bak'
    config['installed_db'] = config['etc_setup'] + '/installed.db'
    config['installed_db_magic'] = 'INSTALLED.DB 2\n'
    
def setup(target):
    '''Create skeleton folder tree, initialize empty installed packages database and fetch current package index'''
    if os.path.exists(target):
        sys.exit('Abort: target path "%s" exists' % target)
    os.makedirs(config['etc_setup'])  
    write_installed({0:{}})                
    # update()                
def get_installed(dummy):
    ''' Get list of installed packages from ./etc/setup/installed.db.
    
    Returns nested dictionary (empty when installed.db doesn't exist):
        {status_int : {pkg_name : archive_name}}
    
    I don't know significance of the nesting or leading zero. It appears to be
    extraneous? The db is just a straight name:tarball lookup table.
    In write_installed() the "status" is hard coded as 0 for all packages.
    '''
    # installed = {0:{}}
    installed = {}
    if os.path.exists(config['installed_db']):
        for i in open (config['installed_db']).readlines ()[1:]:
            name, archive, status = string.split (i)
            # installed[int (status)][name] = archive
            installed[name] = archive
    if dummy:
        print(installed) ##debug
    return installed
def write_installed(packages):
    ''' Record packages in install.db. Packages arg needs to be nested dict {status_int : {name : archive_name}} 
    Reads existing installed list and then rewrites whole file. It would be better to just append?
    '''
    # read existing installed packages
    installed = get_installed('')
    
    if packages == 'debug':
        for k in installed.keys():
            print(k, installed[k])

    file = open (config['installed_db'], 'w')
    file.write (config['installed_db_magic'])
    for k in installed.keys():
        file.writeline('%s %s 0' % (installed[k], installed[k]))
    
'''
    file = open (config['installed_db'], 'w')
    file.write (config['installed_db_magic'])
    file.writelines (map (lambda x: '%s %s 0\n' % (x, installed[0][x]),
                  installed[0].keys ()))
    if file.close ():
        raise 'urg'
'''
    
'''
INSTALLED.DB 2
libxml2 libxml2-2.9.1-1.tar.bz2 0
gdal110dll gdal110dll-1.10.1-1.tar.bz2 0
libtiff libtiff-4.0.2-2.tar.bz2 0
libjpeg12 libjpeg12-6b-3.tar.bz2 0
'''
def main(action, args):
    get_config()
    print('Action: %s' % action)
    print('Parameters: %s' % args)
    if action == 'setup':
        setup(config['root'])
    else:
        eval(action)(args)


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2:])
    # <<globals>>
    # <<parse command line>>
    # <<post-parse globals>>
    # <<run the commands>>
    # <<wrap up>>
