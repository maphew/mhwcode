import argparse
p = argparse.ArgumentParser("a foo bar dustup")
p.add_argument('-i', '--ini', help="use alternate ini file")
print '\n', p.parse_args()

