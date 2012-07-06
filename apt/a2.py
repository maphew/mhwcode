#@+leo-ver=5-thin
#@+node:maphew.20120623001354.1529: * @file a2.py
''' 2nd attempt at using Plac module to drive Apt.
    Adapted from the 'Fake version control system' example:
    http://plac.googlecode.com/hg/doc/plac.html#a-non-class-based-example '''

import plac

commands = 'install','remove','update','setup'

@plac.annotations(packages='package(s) to operate on')
def install(*packages):
    "install packages"
    
    import apt
    print 'apt install', ' '.join(packages)
    apt.dists={'test': {}, 'curr': {}, 'prev' : {}}
    apt.distname='curr'
    apt.distnames = ('curr', 'test', 'prev')
    apt.files=packages
    # for p in packages:
        # apt.packagename=p
        # apt.install()
    apt.packagename='dummy'
    apt.install()
        
    return('Installing ', packages)

@plac.annotations(package='package(s) to operate on')
def remove(*package):
    "Remove packages"
    
    return('Removing ', '  '.join(package))

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
