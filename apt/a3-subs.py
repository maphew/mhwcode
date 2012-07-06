#@+leo-ver=5-thin
#@+node:maphew.20120706121056.1531: * @file a3-subs.py
''' See if we can figure out Plac with sub-commands
    @url http://plac.googlecode.com/hg/doc/plac.html#implementing-subcommands '''

import plac

class AptInterface(object):
    """A minimal interface for Apt command line installer, maybe"""
    commands = 'setup','update','install','remove'

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
    
    
if __name__=='__main__':
    plac.Interpreter(plac.call(AptInterface)).interact()
#@-leo
