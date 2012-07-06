#@+leo-ver=5-thin
#@+node:maphew.20120622231339.1567: * @file a1.py
''' First attempt at using Plac module '''
import plac

@plac.annotations(
    command=("command to run", 'positional', None, str, ['install','remove','update','setup']),
    packages=("list of packages", 'positional', None, str, None, 'pkg'))
    
def main(command, *packages):
    "Operate on packages"
    yield "Running %s on %s" % (command, packages)
    
    if command == 'install':
        yield 'Installing %s' % packages
    elif command == 'remove':
        yield 'Removing %s' % packages
    elif command == 'update':
        yield 'Updating package list from mirror' 
    elif command == 'setup':
        yield 'Initializing new Osgeo4W install' 
    
    
if __name__=='__main__':
    for output in plac.call(main):
        print output
        
#@-leo
