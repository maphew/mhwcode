#@+leo-ver=5-thin
#@+node:maphew.20120623001354.1529: * @file a2.py
''' 2nd attempt at using Plac module to drive Apt.
    Adapted from the 'Fake version control system' example:
    http://plac.googlecode.com/hg/doc/plac.html#a-non-class-based-example '''

import plac, apt, os

commands = 'install','remove','update','setup'

# """Set apt global variables"""
apt.root = os.environ['OSGEO4W_ROOT']
apt.config = apt.root + '/etc/setup/'
apt.setup_ini = apt.config + '/setup.ini'
apt.setup_bak = apt.config + '/setup.bak'
apt.installed_db = apt.config + '/installed.db'
apt.installed_db_magic = 'INSTALLED.DB 2\n'

apt.dists = {'test': {}, 'curr': {}, 'prev' : {}}
apt.distname = 'curr'
apt.distnames = ('curr', 'test', 'prev')
apt.download_p = 0  # download only flag, 1=yes
apt.installed = 0
apt.get_setup_ini()
apt.get_installed()

@plac.annotations(packages='package(s) to operate on')
def install(*packages):
    "install packages"
    
    print 'apt install', ' '.join(packages)
    apt.files=packages
    for p in packages:
        apt.packagename=p
        apt.install()
        
    return('Installing ', packages)

@plac.annotations(packages='package(s) to operate on')
def remove(*packages):
    "Remove packages"

    print 'apt remove', ' '.join(packages)
    # apt.installed = 0
    apt.files=packages
    for p in packages:
        apt.packagename=p
        apt.remove()
        
    return('Removing ', '  '.join(packages))

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
