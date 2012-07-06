#@+leo-ver=5-thin
#@+node:maphew.20120623001354.1529: * @file a2.py
'''2nd attempt at using Plac module, adapted from
the 'Fake version control system' example:
http://plac.googlecode.com/hg/doc/plac.html#a-non-class-based-example'''

import plac

commands = 'install','remove','update','setup'

@plac.annotations(packages='package(s) to operate on')
def install(packages):
    "install packages"
    return('installing ', packages)

@plac.annotations(packages='package(s) to operate on')
def remove(packages):
    "Remove packages"
    return('Removing ', packages)

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
