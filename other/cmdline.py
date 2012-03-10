''' exploring argparse for handling commandline parameters '''
# http://www.doughellmann.com/PyMOTW/argparse/
# http://stackoverflow.com/questions/9642692/argparse-help-without-duplicate-allcaps
# http://stackoverflow.com/questions/5462873/control-formatting-of-the-argparse-help-argument-list
# http://stackoverflow.com/questions/3853722/python-argparse-how-to-insert-newline-the-help-text
# http://stackoverflow.com/questions/4042452/display-help-message-with-python-argparse-when-script-is-called-without-any-argu
#

import sys,argparse
from argparse import RawTextHelpFormatter

def args():
    ''' stub for developing Apt command line argument parser '''
    ''' apt [update, install, remove, setup] [list of packages] '''
    p = argparse.ArgumentParser(
        description='Apt - a commandline package installer for Osgeo4w',
            formatter_class=argparse.RawTextHelpFormatter
##          formatter_class=lambda prog:
##            argparse.HelpFormatter(prog,max_help_position=30)
        )

##    subp = p.add_subparsers(help='commands')
##    list_parser = subp.add_parser('action', help='install update remove setup ...')
##    list_parser.add_argument('dirname', action='store', help='Directory to list')

    actions = "install update remove setup".split()
    p.add_argument('action', choices=actions,
        help="""
install - named packages
remove  - named packages
update  - download latest setup.ini file
setup   - create skeleton file structure
            """)

    p.add_argument('package', action="append", nargs="*",
        help="list of packages to operate on")
    p.add_argument('-i', '--ini',
        help="full path or url to alternate setup.ini")
    p.add_argument('-d', '--download', action="store_true", default=False,
        help="download only, don't install")
    p.add_argument('-m', '--mirror', metavar="MIRROR",
        default="http://download.osgeo.org/osgeo4w",
        help="url of package mirror to download from")
    p.add_argument('-s', '--start-menu', metavar="NAME",
        default="OSGeo4W",
        help="StartMenu folder name to use")
    p.add_argument('-r', '--root',
        default="C:/OSGeo4W",
        help="use this as root directory", metavar="PATH")
    p.add_argument('-x', '--ignore-deps', action="store_true",
        default=False,
        help="ignore dependencies")
    p.add_argument('-v','--version', action='version', version='%(prog)s 0.1')
    print '\n', p.parse_args()

if __name__ == '__main__':
    args()

