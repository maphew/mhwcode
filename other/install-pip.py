"""
pip-install.py

A pure python script to download and install the distribute_setup and
pip utilities

Adapted from:
    http://stackoverflow.com/questions/4750806/how-to-install-pip-on-windows/15294806#15294806
    http://stackoverflow.com/questions/2792650/python3-error-import-error-no-module-name-urllib
    http://stackoverflow.com/questions/1093322/how-do-i-check-what-version-of-python-is-running-my-script


matt wilkie <maphew@gmail.com>
license: X/MIT
2013-Apr-15
http://www.maphew.com/2013/install-pip-script/
"""

import sys

sources = [
    'http://python-distribute.org/distribute_setup.py',
    'https://raw.github.com/pypa/pip/master/contrib/get-pip.py',
    ]

warning = '''\n
    Usage: python %s GO

    This script downloads and executes arbitrary code from the internet.
    It is worth noting this could be extremely dangerous if one doesn't
    have the expertise or bother to inspect the url-file before executing
    these commands.

    At the time of this writing said arbitrary code is:
    ''' % (sys.argv[0])
for s in sources:
    warning = warning + '\n\t %s' % s

if not len(sys.argv) > 1:
    sys.exit(warning)
if not sys.argv[1] == 'GO':
    sys.exit(warning)

if sys.hexversion < 0x03000000:
    from urllib2 import urlopen         # python 2
else:
    from urllib.request import urlopen  # python 3+

for src in sources:
    print('\n %s \n %s \n' % ('-'*78, src))
    f = urlopen(src).read()
    try: exec(f)
    except:
        print('''
        **** Whups. an exception happened in "exec(f)" of %s.
        **** Carrying on anyway,
        **** but you should check to ensure it's not a real problem.
        ''' % sys.argv[0])
    print('\n %s \n %s \n' % (src, '-'*78))

