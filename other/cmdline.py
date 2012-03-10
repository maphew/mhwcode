''' exploring argparse for handling commandline parameters '''
# http://www.doughellmann.com/PyMOTW/argparse/
# http://stackoverflow.com/questions/9642692/argparse-help-without-duplicate-allcaps

import sys,argparse

def args():
	''' stub for developing Apt command line argument parser '''
	''' apt [update, install, remove, setup] [list of packages] '''
	p = argparse.ArgumentParser(description='apt commandline installer for Osgeo4w')
	p.add_argument('action', choices="install update remove setup".split(),
		help="install, update, remove or setup")
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
	#print p.action, p.packages
	#print Namespace


if __name__ == '__main__':
	args()

