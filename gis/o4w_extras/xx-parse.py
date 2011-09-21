#!/usr/bin/env python
# -*- coding: latin-1 -*-#
#@+leo-ver=5-thin
#@+node:maphew.20110914213235.1222: * @file xx-parse.py
#@@first
#@@first
#@@language python
#@@tabwidth -4
#@+others
#@+node:maphew.20110914213235.1221: ** parse command line
__version__ = '2011-09-14.20:47'
# print '-={ %s }=-\n'% (str.strip(svn_id, ' $'))    
#@verbatim
#@url http://www.doughellmann.com/PyMOTW/argparse/

import argparse, sys

# @url http://stackoverflow.com/questions/4042452/display-help-message-with-python-argparse-when-script-is-called-without-any-argum
# display the usage message when it is called with no arguments
class MyParser(argparse.ArgumentParser):
    def error(self, message):
        sys.stderr.write('error: %s\n' % message)
        self.print_help()
        sys.exit(2)

parser=MyParser()
parser.add_argument('action', help='one of "install" or "remove" ')
args = vars(parser.parse_args())

#@-others
#@-leo
