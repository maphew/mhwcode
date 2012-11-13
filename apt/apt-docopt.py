"""apt-docopt

A command line installer for Osgeo4w

Usage:
    apt update
    apt install <package>...
    apt remove  <package>...
    apt setup

Options:
    -d,--download          download only
    -i,--ini=FILE          use setup.ini [default: %osgeo4w_root%/etc/setup/setup.ini]
    -m,--mirror=URL        use mirror [default: http://download.osgeo.org/osgeo4w]
    -r,--root=DIR          set osgeo4w root [default: C:\Osgeo4W]
    -x,--no-deps           ignore dependencies
    -s,--start-menu=NAME   set the start menu name [default: OSGeo4W]
"""
from docopt import docopt


if __name__ == '__main__':
    arguments = docopt(__doc__, version='apt-docopt version 0.1')
    print(arguments)