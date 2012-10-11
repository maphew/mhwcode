#@+leo-ver=5-thin
#@+node:maphew.20120623001354.1529: * @file a2.py
''' 2nd attempt at using Plac module to drive Apt.
    Adapted from the 'Fake version control system' example:
    http://plac.googlecode.com/hg/doc/plac.html#a-non-class-based-example '''

import plac, apt, os, urllib

commands = 'install','remove','update','setup'

# """Set apt global variables"""
apt.INSTALL = 'install'
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

apt.mirror = apt.get_config('last-mirror')  # the url
apt.mirror_dir = urllib.quote (apt.mirror, '').lower () # the local filesystem dir name
apt.last_cache = apt.get_config('last-cache')
apt.downloads = '%s/%s' % (apt.last_cache, apt.mirror_dir)

apt.get_setup_ini() # parse setup.ini into package name, version, etc.
apt.get_installed()


@plac.annotations(packages='package(s) to operate on')
def install(*packages):
    "install packages"

    print '-' *10 + ' running apt install', ' '.join(packages)
    packages = list(packages)
    #packages.insert(0, 'install')
    apt.packages = packages
    # for p in packages:
        # apt.packagename=p
    apt.packagename = packages[0]
    apt.install(packages)

    return('-' *10 + ' Install complete', '')

@plac.annotations(packages='package(s) to operate on')
def remove(*packages):
    "Remove packages"

    print '-' *10 + ' apt remove', ' '.join(packages)
    packages = list(packages)
    # packages.insert(0, 'remove')
    # apt.files=packages
    apt.packages = packages
    # for p in packages:
        # apt.packagename=p
        # apt.remove()
    # apt.packagename=0
    # apt.remove()
    apt.remove(packages)

    return('-' *10 + ' Remove complete', '')

@plac.annotations(message=('commit message', 'option'))
def update(message):
    "download latest packages info from mirror"
    return ('update ', message)

@plac.annotations(quiet=('summary information', 'flag', 'q'))
def setup(quiet):
    "create Osgeo4w filesystem skeleton"
    return ('setup ', quiet)

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

#@-leo
