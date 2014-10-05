''' 2nd attempt at using Plac module to drive Apt.
    Adapted from the 'Fake version control system' example:
    http://plac.googlecode.com/hg/doc/plac.html#a-non-class-based-example 
    
    Basic premise is to import apt as module, then pick and choose the functions
    to run in a plac way.
'''

import plac, apt, os, urllib

commands = 'install','remove','update','setup'

# """Set apt global variables"""
apt.INSTALL = 'install'
apt.check_env() # verify osgeo4w_root is set
apt.OSGEO4W_ROOT = os.environ['OSGEO4W_ROOT']
apt.root = apt.OSGEO4W_ROOT
apt.OSGEO4W_STARTMENU = 'OSGeo4W'
apt.config = apt.root + '/etc/setup/'
apt.setup_ini = apt.config + '/setup.ini'
apt.setup_bak = apt.config + '/setup.bak'
apt.installed_db = apt.config + '/installed.db'
apt.installed_db_magic = 'INSTALLED.DB 2\n'

apt.dists = 0
apt.distname = 'curr'
apt.distnames = ('curr', 'test', 'prev')
apt.download_p = 0  # download only flag, 1=yes
apt.depend_p = 0  # ignore dependencies flag, 1=ignore
apt.installed = 0

apt.last_mirror = apt.get_config('last-mirror')
apt.mirror = apt.get_mirror()  # the url
apt.mirror_dir = urllib.quote (apt.mirror, '').lower () # the local filesystem dir name
apt.last_cache = apt.get_config('last-cache')
apt.downloads = '%s/%s' % (apt.last_cache, apt.mirror_dir)

try:
    apt.get_setup_ini() # parse setup.ini into package name, version, etc.
    apt.get_installed()
        
except:
    print 'Error retreiving installed package info. Has "apt setup" been run yet?\n'
    # apt.check_setup(apt.installed_db, apt.setup_ini) # verify skeleton file structure exists
        
@plac.annotations(packages='list of one or more packages to install')
def install(*packages):
    "install packages"
    print '-' *10 + ' running apt install', ' '.join(packages)
    packages = list(packages)
    apt.install(packages)
    return('-' *10 + ' Install complete', '')

@plac.annotations(packages='package(s) to operate on')
def remove(*packages):
    "Remove packages"
    print '-' *10 + ' running apt remove', ' '.join(packages)
    packages = list(packages)
    apt.remove(packages)
    return('-' *10 + ' Remove complete', '')

@plac.annotations(mirror=('alternate url to use', 'option'))
def update(mirror):
    "download latest packages info from mirror"    
    print '-' *10 + ' running apt update', mirror   
    apt.update()
    return (10*'-'+ 'Update finished ', '')

@plac.annotations()
def setup():
    "create Osgeo4w filesystem skeleton"
    print '-' *10 + ' running apt setup'   
    apt.setup()
    return ('-' *10 + 'setup ', '')

def __missing__(name):
    return('Command %r does not exist' % name,)

def __exit__(etype, exc, tb):
    "Will be called automatically at the end of the interpreter loop"
    if etype in (None, GeneratorExit):  # success
        print('ok')

main = __import__(__name__) # the module imports itself!

if __name__=='__main__':
    import plac
    for out in plac.call(main): print(out)
