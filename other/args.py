"""yet another argparse learning snippet"""
import argparse

# create the top level parser
parser = argparse.ArgumentParser(description='Command line package manager for Osgeo4w')
##parser.add_argument('action', type=str, help='install, update, setup',
##    choices='install update setup'.split())
subparsers = parser.add_subparsers()

##parser.parse_args('install'.split(' '))
##parser.add_argument('package', type=str, nargs='+', help='list of packages')

# global options
parser.add_argument('--ini')
parser.add_argument('--mirror')
parser.add_argument('--download-only')

# install
parser_ins = subparsers.add_parser('install', help='install new packages')
parser_ins.add_argument('package', nargs='+', help='list of packages')

# remove
parser_rem = subparsers.add_parser('remove', help='remove installed packages')
parser_rem.add_argument('package', nargs='+', help='list of packages')

# update
parser_rem = subparsers.add_parser('update',
    help='get latest available package listing from mirror')
parser_rem.add_argument('None')

# setup
parser_rem = subparsers.add_parser('setup',
    help='initialize new Osgeo4W environment')
parser_rem.add_argument('path', help='path to use for Osgeo4W root')



args = parser.parse_args()
##print args.accumulate(args.action)
