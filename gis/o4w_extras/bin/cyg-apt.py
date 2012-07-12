#!/usr/bin/env python

'''
cyg-apt - Cygwin installer to keep cygwin root up to date

(c) 2002--2003  Jan Nieuwenhuizen <janneke@gnu.org>

License: GNU GPL


Port to pure python started July 2008 by Matt.Wilkie@gov.yk.ca
'''

import __main__
import getopt
import os
import glob
import re
import shutil
import string
import sys
import urllib
import gzip, tarfile
import hashlib
import subprocess

# The abi change.
ABI = ''
if 'ABI' in os.environ.keys ():
	ABI = os.environ['ABI']

# OSGEO4W_ROOT = ''
# if 'OSGEO4W_ROOT' in os.environ.keys ():
	# OSGEO4W_ROOT = os.environ['OSGEO4W_ROOT']
	# os.putenv('OSGEO4W_ROOT_MSYS', OSGEO4W_ROOT) # textreplace.exe needs this (post_install)
	# OSGEO4W_ROOT = string.replace(OSGEO4W_ROOT, '\\', '/') # convert backslash to foreslash
# else:
	# sys.stderr.write ('error: Please set OSGEO4W_ROOT\n')
	# sys.exit (2)

# #FIXME: should this really be hardcoded?
# #FIXME:  this only works for English, (e.g. called Startmenu with umlaut in a german windows)
# # related: http://trac.osgeo.org/osgeo4w/ticket/21, http://code.google.com/p/maphew/issues/detail?id=13
# OSGEO4W_STARTMENU = os.environ['USERPROFILE'] + '\Start Menu\Programs\OSGeo4W'
# os.putenv('OSGEO4W_STARTMENU', OSGEO4W_STARTMENU)

root = '/cygwin'
# root = CYGWIN_ROOT

NETREL = '/netrel'
EXTRA = NETREL + '/extra'
# PATCH = NETREL + '/patch'
SRC = NETREL + '/src'
CWD = os.getcwd ()

os.environ['PATH'] = NETREL + '/bin:' + os.environ['PATH']

#mirror = 'http://download.osgeo.org/osgeo4w'
# mirror = 'ftp://mirrors.rcn.net/mirrors/sources.redhat.com/cygwin'
# mirror = 'http://mirrors.rcn.net/pub/sourceware/cygwin'
mirror = 'http://mirror.cpsc.ucalgary.ca/mirror/cygwin.com'

downloads = root + '/var/cache/setup/' + urllib.quote (mirror, '').lower ()

config = root + '/etc/setup/'
setup_ini = config + '/setup.ini'
setup_bak = config + '/setup.bak'
installed_db = config + '/installed.db'
installed_db_magic = 'INSTALLED.DB 2\n'

INSTALL = 'install'


def usage ():
	sys.stdout.write ('''cyg-apt [OPTION]... COMMAND [PACKAGE]...

Commands:
''')
	d = __main__.__dict__
	commands = filter (lambda x:
				type (d[x]) == type (usage) and d[x].__doc__, d)
	sys.stdout.writelines (map (lambda x:
					"    %s - %s\n" % (x, d[x].__doc__),
					psort (commands)))
	sys.stdout.write (r'''
Options:
	-d,--download          download only
	-i,--ini=FILE          use setup.ini [%(setup_ini)s]
	-m,--mirror=URL        use mirror [%(mirror)s]
	-r,--root=DIR          set cygwin root [%(root)s]
	-t,--t=NAME            set dist name (*curr*, test, prev)
	-x,--no-deps           ignore dependencies
''')
			
(options, files) = getopt.getopt (sys.argv[1:],
				'dhi:m:r:t:x',
				('download', 'help', 'mirror=', 'root='
					'ini=', 't=', 'no-deps'))

command = 'help'
if len (files) > 0:
	command = files[0]

packagename = 0
if len (files) > 1:
	packagename = files[1]

distname = 'curr'

depend_p = 0
download_p = 0
for i in options:
	o = i[0]
	a = i[1]

	if 0:
		pass
	elif o == '--download' or o == '-d':
			download_p = 1
	elif o == '--help' or o == '-h':
		command = 'help'
		break
	elif o == '--ini' or o == '-i':
		setup_ini = a
	elif o == '--mirror' or o == '-m':
		mirror = a
	elif o == '--root' or o == '-r':
		root = a
	elif o == '--t' or o == '-t':
		distname = a
	elif o == '--no-deps' or o == '-x':
		depend_p = 1

def version_to_string (t):
	#return '%s-%s' % (string.join (map (lambda x: "%d" % x, t[:-1]), '.'),
	#		  t[-1])
	def try_itoa (x):
		if type (x) == int:
			return "%d" % x
		return x
	return '%s-%s' % (string.join (map (try_itoa, t[:-1]), '.'),
			t[-1])

def string_to_version (s):
	# bash-2.05b-9
	# return map (string.atoi, (string.split (re.sub ('[.-]', ' ', s))))
	s = re.sub ('([^0-9][^0-9]*)', ' \\1 ', s)
	s = re.sub ('[ .-][ .-]*', ' ', s)
	def try_atoi (x):
		if re.match ('^[0-9]*$', x):
			return string.atoi (x)
		return x
	return tuple (map (try_atoi, (string.split (s, ' '))))

def split_ball (p):
	# mc-4.6.0a-20030721-1.tar.bz2
	#m = re.match ('^([^.]*)-([0-9][^-/]*-[0-9][0-9]*)(.tar.bz2)?$', p)
	m = re.match ('^([^.]*)-([0-9].*-[0-9][0-9]*)(.tar.bz2)?$', p)
	return (m.group (1), string_to_version (m.group (2)))

def join_ball (t):
	return t[0] + '-' + version_to_string (t[1])

###########################


def debug (s):
	s

def help ():
	'''help COMMAND'''
	if len (files) < 2:
		usage ()
		sys.exit (0)

	print  __main__.__dict__[packagename].__doc__

dists = 0
distnames = ('curr', 'test', 'prev')
def get_setup_ini ():
	global dists
	if dists:
		return
	dists = {'test': {}, 'curr': {}, 'prev' : {}}
	chunks = string.split (open (setup_ini).read (), '\n\n@ ')
	for i in chunks[1:]:
		lines = string.split (i, '\n')
		name = string.strip (lines[0])
		debug ('package: ' + name)
		packages = dists['curr']
		records = {'sdesc': name}
		j = 1
		while j < len (lines) and string.strip (lines[j]):
			debug ('raw: ' + lines[j])
			if lines[j][0] == '#':
				j = j + 1
				continue
			elif lines[j][0] == '[':
				debug ('dist: ' + lines[j][1:5])
				packages[name] = records.copy ()
				packages = dists[lines[j][1:5]]
				j = j + 1
				continue

			try:
				key, value = map (string.strip,
					string.split (lines[j], ': ', 1))
			except:
				print lines[j]
				raise 'URG'
			if value[0] == '"' and value.find ('"', 1) == -1:
				while 1:
					j = j + 1
					value += lines[j]
					if lines[j].find ('"') != -1:
						break
			records[key] = value
			j = j + 1
		packages[name] = records
		
def get_url ():
	if not dists[distname].has_key (packagename) \
		or not dists[distname][packagename].has_key (INSTALL):
		no_package ()
		install = 0
		for d in distnames:
			if dists[d].has_key (packagename) \
				and dists[d][packagename].has_key (INSTALL):
				install = dists[d][packagename][INSTALL]
				sys.stderr.write ("warning: using [%s]\n" % d)
				break
		if not install:
			sys.stderr.write ("error: %s no install\n" % packagename)
			sys.exit (1)
	else:
		install = dists[distname][packagename][INSTALL]
	file, size, md5 = string.split (install)
	return file, md5

def url ():
	'''print tarball url'''
	print get_url ()[0]

def get_ball ():
	url, md5 = get_url ()
	return '%s/%s' % (downloads, url)

def ball ():
	'''print tarball name'''
	print get_ball ()
	
def down_stat(count, blockSize, totalSize):
	# report download progress
	#courtesy of http://stackoverflow.com/questions/51212/how-to-write-a-download-progress-indicator-in-python
	#FIXME: sometmes percent goes over 100!
	percent = int(count*blockSize*100/totalSize)
	sys.stdout.write("\r...%d%%" % percent)
	sys.stdout.flush()

def do_download ():
	url, md5 = get_url ()
	dir = '%s/%s' % (downloads, os.path.split (url)[0])
	srcFile = os.path.join (mirror + '/' + url)
	dstFile = os.path.join (downloads + '/' + url)
	if not os.path.exists (get_ball ()): #or not check_md5 ():
		print '\nFetching %s' % srcFile
		if not os.path.exists (dir):
			os.makedirs (dir)

	## CHANGED: use urllib instead of wget, was:
	#status = os.system ('cd %s && wget -c %s/%s' % (dir, mirror, url))
	status = urllib.urlretrieve(srcFile, dstFile, down_stat)
	
	### The following is broken because of urllib change,
	### maybe not needed?
	## successful pipe close returns 'None'
	#if not status:
	#   status = 0
	#signal = 0x0f + status
	### exit_status = status >> 8
	#if status:
	#   raise 'urg'

def download ():
	'''download package'''
	do_download ()
	ball ()
	print
	md5 ()
	
def no_package (s='error'):
	sys.stderr.write ("%s: %s not in [%s]\n" % (s, packagename, distname))

def get_requires ():
	dist = dists[distname]
	if not dists[distname].has_key (packagename):
		no_package ('warning')
		#return []
		sys.exit (1)
	if depend_p:
		return [packagename]
	reqs = {packagename:0}
	n = 0
	while len (reqs) > n:
		n = len (reqs)
		for i in reqs.keys ():
			if not dist.has_key (i):
				sys.stderr.write ("error: %s not in [%s]\n" \
						% (i, distname))
				if i != packagename:
					del reqs[i]
				continue
			reqs[i] = '0'
			p = dist[i]
			if not p.has_key ('requires'):
				continue
			reqs.update (dict (map (lambda x: (x, 0),
						string.split (p['requires']))))
	return reqs.keys ()

def requires ():
	'''print requires: for package'''
	print string.join (get_requires (), '\n')

installed = 0
def get_installed ():
	global installed
	if installed:
		return installed
	installed = {0:{}}
	for i in open (installed_db).readlines ()[1:]:
		name, ball, status = string.split (i)
		installed[int (status)][name] = ball
	return installed

def write_installed ():
	file = open (installed_db, 'w')
	file.write (installed_db_magic)
	file.writelines (map (lambda x: '%s %s 0\n' % (x, installed[0][x]),
					installed[0].keys ()))
	if file.close ():
		raise 'urg'

def get_field (field, default=''):
	for d in (distname,) + distnames:
		if dists[d].has_key (packagename) \
			and dists[d][packagename].has_key (field):
			return dists[d][packagename][field]
	return default

def psort (lst):
	plist.sort (lst)
	return lst

#urg
plist = list
def list ():
	'''installed packages'''
	global packagename
	for packagename in psort (installed[0].keys ()):
		ins = get_installed_version ()
		new = 0
		if dists[distname].has_key (packagename) \
			and dists[distname][packagename].has_key (INSTALL):
			new = get_version ()
		s = '%-20s%-15s' % (packagename, version_to_string (ins))
		if new and new != ins:
			s += '(%s)' % version_to_string (new)
		print s

# CHANGED: pythonized rm,mv,wget which do not always exist on windows
def update ():
	'''setup.ini'''
	if not os.path.exists (downloads):
		os.makedirs (downloads)

	# remove cached ini
	if os.path.exists (downloads + 'setup.ini'):
		os.remove (downloads + 'setup.ini')

	# get current ini
	f = urllib.urlretrieve(mirror + '/setup.ini', downloads + 'setup.ini', down_stat)

	if os.path.exists (setup_ini):
		# backup existing setup config
		if os.path.exists (setup_bak):
				os.remove (setup_bak)
		os.rename (setup_ini, setup_bak)

	# move new setup to config
	os.rename(downloads + 'setup.ini', setup_ini)

def get_version ():
	if not dists[distname].has_key (packagename) \
		or not dists[distname][packagename].has_key (INSTALL):
		no_package ()
		return (0, 0)
		
	package = dists[distname][packagename]
	if not package.has_key ('ver'):
		file = string.split (package[INSTALL])[0]
		ball = os.path.split (file)[1]
		package['ver'] = split_ball (ball)[1]
	return package['ver']
	
def get_installed_version ():
	return split_ball (installed[0][packagename])[1]

def version ():
	'''print installed version'''
	global packagename
	for packagename in psort (installed[0].keys ()):
		if not installed[0].has_key (packagename):
			global distname
			distname = 'installed'
			no_package ()
			sys.exit (1)
		print '%-20s%-12s' % (packagename,
				version_to_string (get_installed_version ()))
	
def get_new ():
	global packagename
	lst = []
	for packagename in installed[0].keys ():
		new = get_version ()
		ins = get_installed_version ()
		if new > ins:
			debug (" %s > %s" % (new, ins))
			lst.append (packagename)
	return lst

def new ():
	'''list new packages in distribution'''
	#print string.join (get_new (), '\n')
	global packagename
	for packagename in psort (get_new ()):
		print '%-20s%-12s' % (packagename,
						version_to_string (get_version ()))
		
		
def md5 ():
	'''check md5 sum'''
	url, md5 = get_url ()
	ball = os.path.basename (url)
	print '%s  %s - remote md5 sum' % (md5, ball)
	# make sure we md5 the *file* not the *filename*
	# kudos to http://www.peterbe.com/plog/using-md5-to-check-equality-between-files
	localFile = file(os.path.join(downloads, url), 'rb')
	my_md5 = hashlib.md5(localFile.read()).hexdigest()

	print '%s  %s - local md5 sum, must match remote to continue' % (my_md5, ball)
	if md5 != my_md5:
		raise 'URG'
	
def search ():
	'''search package list'''
	global packagename
	regexp = packagename
	packages = []
	keys = []
	if distname in dists:
		keys = dists[distname].keys ()
	else:
		for i in dists.keys ():
			for j in dists[i].keys ():
				if not j in keys:
					keys.append (j)
	for i in keys:
		if not regexp or re.search (regexp, i):
			if distname in dists:
				if dists[distname][i].has_key (INSTALL):
					packages.append (i)
			else:
				packages.append (i)
	for packagename in psort (packages):
		s = packagename
		d = get_field ('sdesc') 
		if d:
			s += ' - %s' % d[1:-1]
		print s

def get_missing ():
	reqs = get_requires ()
	lst = []
	for i in reqs:
		if not installed[0].has_key (i):
			lst.append (i)
	if lst and packagename not in lst:
		sys.stderr.write ('warning: missing packages: %s\n' % string.join (lst))
	elif installed[0].has_key (packagename):
		ins = get_installed_version ()
		new = get_version ()
		if ins >= new:
			sys.stderr.write ('%s is already the newest version\n' % packagename)
			#lst.remove (packagename)
		elif packagename not in lst:
			lst.append (packagename)
	return lst

def missing ():
	'''print missing dependencies'''
	print string.join (get_missing (), '\n')

# CHANGED: pythonized tar
def do_install ():
	# find ball
	ball = get_ball ()
	## was:


	#pipe = os.popen ('tar -C %s -xjvf %s' % (root, ball), 'r')
	os.chdir (root)
	pipe = tarfile.open (ball,'r:bz2')
	## was:
	#lst = map (string.strip, pipe.readlines ())
	lst = pipe.getnames()
	pipe.extractall()
	pipe.close()

	if pipe.close ():
		raise 'urg'
	# record list of files installed

	write_filelist (lst)
	
	# configure...
	if os.path.isdir ('%s/etc/postinstall' % root):
		## was:
		#post = os.listdir ('%s/etc/postinstall' % root)
		post = glob.glob ('%s/etc/postinstall/*.bat' % root)
		if post:
			#print '\nThe tasks below are unfinished, please follow up manually:'
			#sys.stderr.write ('not run:\t%s' % string.join (map (lambda x: '%s' % x, post)))
			#print
			post_install () # CHANGED: run postinstall .bat automatically
	#update installed[]
	installed[0][packagename] = os.path.basename (ball)
	# write installed.db
	write_installed ()

# NEW
def post_install ():
	# for postinstall *.bat: run x.bat, rename x.bat x.bat.done
	# adapted from "17.1.3.3 Replacing os.system()"
	# http://www.python.org/doc/2.5.2/lib/node536.html
	
	# TODO: add Start Menu and Desktop links to installed list.

	os.chdir(root)

	# necessary for textreplace, xmklink
	os.putenv('PATH', '%s\\bin' % os.path.normpath(OSGEO4W_ROOT))

	for bat in glob.glob ('%s/etc/postinstall/*.bat' % root):
		try:
			retcode = subprocess.call (bat, shell=True)
			if retcode < 0:
			print >>sys.stderr, "Child was terminated by signal", -retcode
			else:
			os.rename (bat, bat + '.done')

			# harmonize path to match format in etc/setup/pkg-foo.gz
			bat = bat.replace (root, '')         # strip C:\osgeo4w
			bat = bat.replace ('\\','/')         # backslash to foreslash
			bat = bat.replace ('/etc/', 'etc/')  # strip leading slash
			
			# also change foo.bat --> .done in pkg-foo.gz
			lst = get_filelist()
			lst.remove(bat)
			lst.append(bat + '.done')
			write_filelist (lst)

			print >>sys.stderr, "Post_install complete, return code", retcode

		except OSError, e:
			print >>sys.stderr, "Execution failed:", e
# CHANGED: pythonized gzip
def get_filelist ():
	os.chdir (config)
	pipe = gzip.open (config + packagename + '.lst.gz', 'r')
	lst = map (string.strip, pipe.readlines ())
	if pipe.close ():
		raise 'urg'
	return lst

# CHANGED: pythonized gzip
def write_filelist (lst):
	os.chdir(config)
	pipe = gzip.open (packagename + '.lst.gz','w')

	for i in lst:
		pipe.write (i)
		pipe.write ('\n')
	if pipe.close ():
		raise 'urg'

def do_uninstall ():
	# find list
	lst = get_filelist ()
	
	# remove files
	# FIXME: etc/postinstall/*bat.done files are missed because they are in etc/setup/%pkg%.gz as *.bat
	for i in lst:
		file = os.path.join (root, i)
		if not os.path.exists (file):
			sys.stderr.write ('warning: %s no such file\n' % file)
		elif not os.path.isdir (file):
			if os.remove (file):
				raise 'urg'

	# TODO: remove empty dirs?
	# TODO: clear list?
	write_filelist ([])
	# update installed[]
	del (installed[0][packagename])
	write_installed ()

def remove ():
	'''uninstall packages'''
	global packagename
	for packagename in files[1:]:
		if not installed[0].has_key (packagename):
			sys.stderr.write ('warning: %s not installed\n' % packagename)
			continue
		sys.stderr.write ('removing %s %s\n' \
				% (packagename,
					version_to_string (get_installed_version ())))
		do_uninstall ()
	
def install ():
	'''download and install packages with dependencies'''
	global packagename
	missing = {}
	for packagename in files[1:]:
		missing.update (dict (map (lambda x: (x, 0), get_missing ())))
	if len (missing) > 1:
		sys.stderr.write ('to install: \n')
		sys.stderr.write ('    %s' % string.join (missing.keys ()))
		sys.stderr.write ('\n')
	for packagename in missing.keys ():
		download ()
	if download_p:
		sys.exit (0)
	for packagename in missing.keys ():
		if installed[0].has_key (packagename):
			sys.stderr.write ('preparing to replace %s %s\n' \
					% (packagename,
						version_to_string (get_installed_version ())))
			do_uninstall ()
		sys.stderr.write ('installing %s %s\n' \
				% (packagename,
					version_to_string (get_version ())))
		do_install ()

def upgrade ():
	'''all installed packages'''
	files[1:] = get_new ()
	install ()

def setup ():
	'''cygwin environment'''
	if not os.path.isdir (root):
		sys.stderr.write ('Root dir not found, creating %s\n' % root)
		os.makedirs (root)
		## mhw: if root doesn't exist create it. Old approach to just quit is below:
		#sys.stderr.write ('error: %s no root dir\n' % root)
		#sys.exit (2)
	if not os.path.isdir (config):
		sys.stderr.write ('creating %s\n' % config)
		os.makedirs (config)
	if not os.path.isfile (installed_db):
		sys.stderr.write ('creating %s\n' % installed_db)
		global installed
		installed = {0:{}}
		write_installed ()
	if not os.path.isfile (setup_ini):
		sys.stderr.write ('getting %s\n' % setup_ini)
		update ()

##TODO: remove do_unpack, do_build, build, source ??
## osgeo4w does not provide a build environment
## but maybe will later?

#FIXME: pythonize gzip, tar, etc.
def do_unpack ():
	# find ball
	ball = get_ball ()
	# untar capture list
	# tarfile
	#pipe = os.popen ('tar -C %s -xjvf %s' % (CWD, ball), 'r')

	global packagename
	basename = os.path.basename (ball)
	packagename = re.sub ('(-src)*\.tar\.(bz2|gz)', '', basename)
			
	if os.path.exists ('%s/%s' % (SRC, packagename)):
		return

	pipe = os.popen ('tar -C %s -xjvf %s' % (SRC, ball), 'r')
	lst = map (string.strip, pipe.readlines ())
	if pipe.close ():
		raise 'urg1'
	print ('%s/%s' % (SRC, packagename))
	if not os.path.exists ('%s/%s' % (SRC, packagename)):
		raise 'urg2'

def do_build ():
	src = '%s/%s' % (SRC, packagename)
	if not os.path.exists (src):
		raise 'urg'

	m = re.match ('^(.*)-([0-9]*)$', packagename)
	if not m:
		raise 'urg'
	namever = m.group (1)

	package = split_ball (packagename)
	name = package[0]
	#namever = name + '-' + string.join (package[1][1:-1], '.')
	pbuild = package[1][-1]

	# ugh: mknetrel should source <src>/cygwin/mknetrel
	# copy to mknetrel's EXTRA dir for now
	cygwin = src + '/cygwin'
	script = cygwin + '/mknetrel'
	if os.path.exists (script):
		shutil.copy (script, '%s/%s' % (EXTRA, namever))
		
	os.system ('mknetrel %s' % namever)
	
def build ():
	'''build package from source in CWD'''
	global packagename
	if not packagename:
		packagename = os.path.basename (CWD)
	do_build ()
	
def source ():
	'''download, build and install'''
	global packagename
	# let's not do dependencies
	#for packagename in missing.keys ():
	global INSTALL
	INSTALL = 'source'
	for packagename in files[1:]:
		download ()
	for packagename in files[1:]:
		do_unpack ()
		do_build ()
	if 1 or download_p:
		sys.exit (0)

def find ():
	'''package containing file'''
	global packagename
	regexp = re.sub ('^%s/' % root, '/', packagename)
	hits = []
	for packagename in psort (installed[0].keys ()):
		for i in get_filelist ():
			if re.search (regexp, '/%s' % i):
				hits.append ('%s: /%s' % (packagename, i))
	print (string.join (hits, '\n'))

if command == 'setup':
	setup ()
	sys.exit (0)

if command == 'update':
	update ()
	sys.exit (0)

for i in (installed_db, setup_ini):
	if not os.path.isfile (i):
		sys.stderr.write ('error: %s no such file\n' % i)
		sys.stderr.write ('error: set ABI and run cyg-apt setup\n')
		sys.exit (2)
	
get_setup_ini ()
get_installed ()

if command and command in __main__.__dict__:
	__main__.__dict__[command] ()
