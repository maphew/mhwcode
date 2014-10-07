#!/usr/bin/env python
#@+leo-ver=5-thin
#@+node:maphew.20120709214653.1686: * @file apt.py
#@@first
#@+<<docstring>>
#@+node:maphew.20100307230644.3846: ** <<docstring>>
'''
  cyg-apt - Cygwin installer to keep cygwin root up to date

  (c) 2002--2003  Jan Nieuwenhuizen <janneke@gnu.org>

  License: GNU GPL


  Modified by Matt.Wilkie@gov.yk.ca for OSGeo4W,
  beginning July 2008

'''
apt_version = 'Dev - 2014-Oct'
#@-<<docstring>>
#@@language python
#@@tabwidth -4
#@+<<imports>>
#@+node:maphew.20100307230644.3847: ** <<imports>>
import __main__
import getopt
import os
import glob
import re
import shutil
import string
import sys
import urllib
import gzip, tarfile, bz2
import hashlib
import subprocess
import shlex
#@-<<imports>>
#@+others
#@+node:maphew.20100223163802.3718: ** usage
###########################
#Usage
###########################
def usage ():
    # global setup_ini
    # global mirror
    # global root
    print('-={ %s }=-\n'% apt_version)
    # FIXME: list only usable command line parameters, not all functions
    # SOLVED: omit '''comment''' after function name, only those are listed
      # better:  use parsopt instead, #53 http://trac.osgeo.org/osgeo4w/ticket/53
    sys.stdout.write ('''apt [OPTION]... COMMAND [PACKAGE]...

Commands:
    available -  show packages available to be installed
    ball - print full path name of package archive
    download - download package
    find - package containing file (from installed packages)
    help - show help for COMMAND
    install - download and install packages, including dependencies
    list - installed packages
    listfiles - installed with package X
    md5 - check md5 sum
    missing - print missing dependencies for X
    new - list available upgrades to currently installed packages
    remove - uninstall packages
    requires - report package dependencies
    search - search available packages list for X
    setup - skeleton installed packages environment
    update - setup.ini
    upgrade - all installed packages
    url - print package archive path, relative to mirror root
    version - print installed version of X
    versions - print versions of all installed packages

Options:
    -d,--download          download only
    -i,--ini=FILE          use setup.ini [%(setup_ini)s]
    -m,--mirror=URL        use mirror [%(mirror)s]
    -r,--root=DIR          set osgeo4w root [%(root)s]
    -t,--t=NAME            set dist name (*curr*, test, prev)
    -x,--no-deps           ignore dependencies
    -s,--start-menu=NAME   set the start menu name (OSGeo4W)
''' % {'setup_ini':setup_ini,'mirror':mirror,'root':root}) #As they were just printing as "%(setup_ini)s" etc...
#@+node:maphew.20121113004545.1577: ** check_env
def check_env():
    #'''Verify we're runnining in an Osgeo4W ready shell'''
    OSGEO4W_ROOT = ''
    if 'OSGEO4W_ROOT' in os.environ.keys ():
        OSGEO4W_ROOT = os.environ['OSGEO4W_ROOT']
        os.putenv('OSGEO4W_ROOT_MSYS', OSGEO4W_ROOT) # textreplace.exe needs this (post_install)
        OSGEO4W_ROOT = string.replace(OSGEO4W_ROOT, '\\', '/') # convert 2x backslash to foreslash
    else:
       sys.stderr.write ('error: Please set OSGEO4W_ROOT\n')
       sys.exit (2)
       
    return OSGEO4W_ROOT
#@+node:maphew.20121111221942.1497: ** check_setup
def check_setup(installed_db, setup_ini):
    #'''Look to see if the installed packages db and setup.ini are avialable'''
    for i in (installed_db, setup_ini):
        if not os.path.isfile (i):
            sys.stderr.write ('error: %s no such file\n' % i)
            sys.stderr.write ('error: set OSGEO4W_ROOT and run "apt setup"\n')
            sys.exit (2)
#@+node:maphew.20100302221232.1487: ** Commands
###########################
#COMMANDS
###########################
#@+node:maphew.20100223163802.3719: *3* available
def available(foo):
    ''' show packages available to be installed'''

    # TODO: this function requires a parameter only because of the command calling
     # structure of the module. The parameter is not used. When the command
     # structure is fixed remove the parameter (or perhaps make it useful by
     # saying (available(at_url_of_package_mirror_x)`

    # courtesy of Aaron Digulla,
    # http://stackoverflow.com/questions/1524126/how-to-print-a-list-more-nicely

    # All packages mentioned in setup.ini
    # TODO: pass distribution as parameter instead of hardcoding
    list = dists['curr'].keys()

    # mark installed packages
    for pkg in installed[0].keys():
        list.remove(pkg)
        list.append('%s*' % pkg)

    # Report to user
    print '\n Packages available to install (* = already installed)\n'
    list = sorted(list)
    split = len(list)/2
    col1 = list[0:split]
    col2 = list[split:]
    for key, value in zip(col1,col2):
        print '%-20s\t\t%s' % (key, value)

#@+node:maphew.20100223163802.3720: *3* ball
def ball (packagename):
    '''print full path name of package archive'''

    # FIXME: really need to find a better name for this command. Not so many
    # understand 'ball' refers to 'tarball', a onetime common moniker for an
    # archive file

    # when called as a command, e.g. "apt ball iconv", pkg is a list
    # when called from another function pkg is a string
    if type(packagename) == str:
        print "\n%s = %s" % (packagename, get_ball (packagename))
    else:
        for p in packagename:
            print "\n%s = %s" % (p, get_ball (p))

#@+node:maphew.20100223163802.3721: *3* download
def download (packagename):
    '''download package'''
    # print sys.argv[0], ": in download() with", packagename

    # # deadweight, not used; equiv feedback should be given by parameter checking earlier
    # if not packagename:
        # sys.stderr.write ('No package specified. Try running "apt available"')

    do_download (packagename)
    ball (packagename)
    print
    md5 (packagename)
    
#@+node:maphew.20100223163802.3722: *3* find
def find ():
    '''package containing file (from installed packages)'''
    global packagename
    if not packagename:
        sys.stderr.write ('Find what? Enter a filename to look for (partial is ok).')
        return

    regexp = re.sub ('^%s/' % root, '/', packagename)
    hits = []
    for packagename in sorted (installed[0].keys ()):
        for i in get_filelist ():
            if re.search (regexp, '/%s' % i, re.IGNORECASE):
                hits.append ('%s: /%s' % (packagename, i))
    print (string.join (hits, '\n'))

#@+node:maphew.20100223163802.3723: *3* help
def help ():
    '''show help for COMMAND'''
    # FIXME: only shows regular help, should show *additional* help
        
    # if "help for..." not present then just show general help.
    if len (params) < 2:
        usage ()
        sys.exit (0)

    action = params[1]
    print  __main__.__dict__[action].__doc__

#@+node:maphew.20100223163802.3724: *3* install
def install (packages):
    '''download and install packages, including dependencies'''
    missing = {}
    # print '=== pkgs:', packages # debug
    for packagename in packages:
        # print packagename
        missing.update (dict (map (lambda x: (x, 0), get_missing (packagename))))
    if len (missing) > 1:
        sys.stderr.write ('to install: \n')
        sys.stderr.write ('    %s' % string.join (missing.keys ()))
        sys.stderr.write ('\n')

    for packagename in missing.keys (): # FIXME: re-use of `packagename` for different purpose is confusing
        download (packagename)

    if download_p:  # quit if download only flag is set
        sys.exit (0)

    install_next(missing.keys (), set([]), set([]))
#@+node:maphew.20100510140324.2366: *4* install_next (missing_packages)
def install_next (missing_packages, resolved, seen):
##    global packagename
    for miss_package in missing_packages:
        if miss_package in resolved:
            continue
        seen.add(miss_package)
        packagename = miss_package
        dependences = get_missing(packagename)
        dependences.remove(miss_package)
        for dep in dependences:
            if dep in resolved:
                continue
            if dep in seen:
                raise Exception(
                    'Required package %s from %s is a circular reference '
                    'with a previous dependent' % (dep, packagename)
                )
            install_next(dependences, resolved, seen)
        packagename = miss_package
        if installed[0].has_key (miss_package):
            sys.stderr.write ('preparing to replace %s %s\n' \
                      % (miss_package,
                         version_to_string (get_installed_version (packagename))))
            do_uninstall (packagename)
        sys.stderr.write ('installing %s %s\n' \
                  % (miss_package,
                     version_to_string (get_version (packagename))))
        do_install (packagename)
        resolved.add(miss_package)
#@+node:maphew.20100223163802.3725: *3* list
def list (foo):
    '''installed packages'''
    # fixme: once again, 'foo' defined but not used. fix after calling structure is refactored
    ## global packagename
    for packagename in sorted (installed[0].keys ()):
        ins = get_installed_version (packagename)
        new = 0
        if dists[distname].has_key (packagename) \
           and dists[distname][packagename].has_key (INSTALL):
            new = get_version (packagename)
        s = '%-20s%-15s' % (packagename, version_to_string (ins))
        if new and new != ins:
            s += '(%s)' % version_to_string (new)
        print s

#@+node:mhw.20120404170129.1475: *3* listfiles
def listfiles ():
    '''installed with package X'''
    if not packagename:
        sys.stderr.write ('No package specified. Try running "apt list"')
        return

    for i in get_filelist():
        print i

#@+node:maphew.20100223163802.3726: *3* md5
def md5 (packagename):
    '''check md5 sum'''
    if not packagename:
        sys.stderr.write ('No package specified. Try running "apt list"')
        return

    url, md5 = get_url (packagename)
    ball = os.path.basename (url)
    print '%s  %s - remote' % (md5, ball)

    # make sure we md5 the *file* not the *filename*
    # kudos to http://www.peterbe.com/plog/using-md5-to-check-equality-between-files
    localFile = file(get_ball(packagename), 'rb')
    my_md5 = hashlib.md5(localFile.read()).hexdigest()

    print '%s  %s - local' % (my_md5, ball)
    if md5 != my_md5:
        raise TypeError('file md5 does not match for ' + ball)

#@+node:maphew.20100223163802.3727: *3* missing
def missing ():
    '''print missing dependencies for X'''
    # FIXME: this would be more useful if it found missing for everything,
    # not just the named package
    if not packagename:
        sys.stderr.write ('No package specified. Try running "apt list"')
        return

    print string.join (get_missing (), '\n')

#@+node:maphew.20100223163802.3728: *3* new
def new (dummy):
    '''list available upgrades to currently installed packages'''
    print '\nThe following packages are newer than the installed version:'
    global packagename
    for packagename in sorted (get_new ()):
        print '%-20s%-12s' % (packagename,
                      version_to_string (get_version (packagename)))

#@+node:maphew.20100223163802.3729: *3* remove
def remove (packages):
    '''uninstall packages'''
##    global packagename
    if not packages:
        sys.stderr.write ('No package(s) specified. Run "apt list" to see installed packages')
        return

    for packagename in packages:
        print packagename
        if not installed[0].has_key (packagename):
            sys.stderr.write ('warning: %s not installed\n' % packagename)
            continue
        sys.stderr.write ('removing %s %s\n' \
                  % (packagename,
                     version_to_string (get_installed_version (packagename))))
        do_uninstall (packagename)

#@+node:maphew.20100223163802.3730: *3* requires
def requires ():
    '''report package dependencies'''
    if not packagename:
        sys.stderr.write ('Please specify a package name.')
        return

    depends = get_requires()
    depends.sort()
    # display as vertical list, one item per line.
    print string.join(depends, '\n')
    ## display as horizontal list, all on one line
    #print string.join (depends)
#@+node:maphew.20100223163802.3731: *3* search
def search ():
    '''search available packages list for X'''
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
    for packagename in sorted (packages):
        s = packagename
        d = get_field ('sdesc')
        if d:
            s += ' - %s' % d[1:-1]
        print s
#@+node:maphew.20100223163802.3732: *3* setup
def setup ():
    '''skeleton installed packages environment'''
    if not os.path.isdir (root):
        sys.stderr.write ('Root dir not found, creating %s\n' % root)
        os.makedirs (root)
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

#@+node:maphew.20100223163802.3733: *3* update
def update ():
    '''setup.ini'''
    if not os.path.exists (downloads):
        os.makedirs (downloads)

    source = mirror + '/setup.ini.bz2'
    archive = downloads + 'setup.ini.bz2'

    # backup existing setup config
    if os.path.exists (setup_ini):
        if os.path.exists (setup_bak):
                os.remove (setup_bak)
        os.rename (setup_ini, setup_bak)

   # remove cached ini
    if os.path.exists (archive):
        os.remove (archive)

   # get current ini
    f = urllib.urlretrieve(source, archive, down_stat)
    uncompressedData = bz2.BZ2File(archive).read()

    # save uncompressed ini to setup dir
    ini = open(setup_ini, 'w')
    ini.write(uncompressedData)
    ini.close

#@+node:maphew.20100223163802.3734: *3* upgrade
def upgrade (dummy):
    '''all installed packages'''
    packages = get_new ()
    install (packages)

#@+node:maphew.20100223163802.3735: *3* url
def url ():
    '''print package archive path, relative to mirror root'''
    print get_url ()[0]

#@+node:maphew.20100223163802.3736: *3* version
def version ():
    '''print installed version of X'''
    global packagename
    if not packagename:
        sys.stderr.write ('No package specified. Try running "apt list"')
        return

    print '%-20s%-12s' % (packagename,
             version_to_string (get_installed_version ()))

#@+node:mhw.20120404170129.1476: *3* versions
def versions ():
    '''print versions of all installed packages'''
    global packagename

    for packagename in sorted (installed[0].keys ()):
        if not installed[0].has_key (packagename):
            global distname
            distname = 'installed'
            no_package ()
            sys.exit (1)
        print '%-20s%-12s' % (packagename,
                 version_to_string (get_installed_version ()))
#@+node:maphew.20100302221232.1485: ** Helper functions
###########################
#Helper functions
###########################
#@+node:maphew.20100223163802.3737: *3* cygpath
def cygpath(path):
    # change dos path to unix style path, plus add cygwin prefix
    # needs some changes to work for osgeo4w
    # adapted from http://cyg-apt.googlecode.com: cygpath()
    path = path.replace("\\", "/")
    if len(path) == 3:
        if path[1] == ":":
            path = "/" + path[0].lower()
    elif len(path) > 1:
        if path[1] == ":":
            path = "/" + path[0].lower() + path[2:]
    return path

#@+node:maphew.20100223163802.3738: *3* debug
def debug (s):
    # still haven't figured out quite how this is meant to be used
    # uncomment the print statement to display contents of parsed setup.ini
    s
    #print s

#@+node:maphew.20100308085005.1379: ** Doers
#@+node:maphew.20100223163802.3739: *3* do_download
def do_download (packagename):
    # CHANGED: pythonized tar
    #        : only print % downloaded if > than last time (lpinner)
    
    # print sys.argv[0], ": in do_download() with", packagename

    url, md5 = get_url (packagename)   # md5 is retrieved but not used, remove from function?

    dir = '%s/%s' % (downloads, os.path.split (url)[0])
    srcFile = os.path.join (mirror + '/' + url)
    dstFile = os.path.join (downloads + '/' + url)

    if not os.path.exists (get_ball (packagename)): #or not check_md5 ():
        print '\nFetching %s' % srcFile

        if not os.path.exists (dir):
            os.makedirs (dir)
        status = urllib.urlretrieve(srcFile, dstFile, down_stat)
#@+node:maphew.20100223163802.3742: *4* down_stat
def down_stat(count, blockSize, totalSize):
    # ''' Report download progress '''
    #courtesy of http://stackoverflow.com/questions/51212/how-to-write-a-download-progress-indicator-in-python
    percent = int(count*blockSize*100/totalSize+0.5)#Round percentage

    if not 'last_percent' in vars(down_stat):down_stat.last_percent=0 #Static var to track percentages so we only print N% once.

    if percent > 100:    # filesize usually doesn't correspond to blocksize multiple, so flatten overrun
        percent = 100
        down_stat.last_percent=0

    if percent > down_stat.last_percent:
        sys.stdout.write("\r...%d%%  " % percent)
        sys.stdout.flush()
    down_stat.last_percent=percent
#@+node:maphew.20100223163802.3740: *3* do_install
def do_install (packagename):
    # ''' Unpack the package in appropriate locations, write file list to installed manifest, run postinstall confguration. '''

    # retrieve local package (ball) and check md5
    ball = get_ball (packagename)

    # unpack
    os.chdir (root)
	# very strange, on some files opening the tarfile with bz2 argument doesn't work
	# http://lists.osgeo.org/pipermail/osgeo4w-dev/2011-January/001202.html
	# in any case the docs say transparent decompression via plain 'r' is recommended.
	#   http://docs.python.org/library/tarfile.html
    #pipe = tarfile.open (ball,'r:bz2')
    pipe = tarfile.open(ball,'r')
    lst = pipe.getnames()
    pipe.extractall()
    pipe.close()
    if pipe.close ():
        raise TypeError('urg')

   # record list of files installed
    write_filelist (packagename, lst)

    # configure...
    if os.path.isdir ('%s/etc/postinstall' % root):
        post = glob.glob ('%s/etc/postinstall/*.bat' % root)
        if post:
            post_install (packagename)

    #update package details in installed.db
    installed[0][packagename] = os.path.basename (ball)
    write_installed ()
#@+node:maphew.20100223163802.3741: *3* do_uninstall
def do_uninstall (packagename):
    # ''' For package X: delete installed files & remove from manifest, remove from installed.db '''
    # TODO: remove empty dirs?
    do_run_preremove(root, packagename)

    # retrieve list of installed files
    lst = get_filelist (packagename)

    # delete files
    for i in lst:
        file = os.path.abspath (os.path.join(root,i))
        if not os.path.exists (file):
            sys.stderr.write ('warning: %s no such file\n' % file)
        elif not os.path.isdir (file):
            try:
                os.remove(file)
            except WindowsError:
                os.chmod(file, 0777) # remove readonly flag and try again
                os.remove (file)
            else:
                sys.stdout.write('removed: %s\n' % file)

    # clear from manifest
    write_filelist (packagename, [])

    # remove package details from installed.db
    del (installed[0][packagename])
    write_installed ()

#@+node:maphew.20120222135111.1873: *3* do_run_preremove
def do_run_preremove(root, packagename):
    # ''' Run the etc/preremove batch files for this package '''
    for bat in glob.glob ('%s/etc/remove/%s.bat' % (root, packagename)):
        try:
            retcode = subprocess.call (bat, shell=True)
            if retcode < 0:
                print >>sys.stderr, "Child was terminated by signal", retcode

            print >>sys.stderr, "Post_install complete, return code", retcode

        except OSError, e:
            print >>sys.stderr, "Execution failed:", e
#@+node:maphew.20100308085005.1380: ** Getters
#@+node:maphew.20100223163802.3743: *3* get_ball
def get_ball (packagename):
    url, md5 = get_url (packagename)
    return '%s/%s' % (downloads, url)

#@+node:maphew.20100223163802.3744: *3* get_field
def get_field (field, default=''):
    for d in (distname,) + distnames:
        if dists[d].has_key (packagename) \
           and dists[d][packagename].has_key (field):
            return dists[d][packagename][field]
    return default

#@+node:maphew.20100223163802.3745: *3* get_filelist
def get_filelist (packagename):
    # ''' Retrieve list of files installed for package X from manifest (/etc/setup/package.lst.gz)'''
    os.chdir (config)
    pipe = gzip.open (config + packagename + '.lst.gz', 'r')
    lst = map (string.strip, pipe.readlines ())
    if pipe.close ():
        raise TypeError('urg')
    return lst

#@+node:maphew.20100223163802.3746: *3* get_installed
def get_installed ():
    ''' Get list of installed packages from ./etc/setup/installed.db.
    
    Returns nested dictionary (empty when installed.db doesn't exist):
    {status_int : {pkg_name : archive_name}}
    
    I don't know significance of the nesting or leading zero. It appears to be
    extraneous? The db is just a straight name:tarball lookup table.
    In write_installed() the "status" is hard coded as 0 for all packages.
    '''
    
    global installed
    
    # I think the intent here is for performance,
    # don't reread from disk for every invocation.
    # I'm not sure that's wise. What if setup.exe
    # has modified it in the interim? Or another 
    # apt instance?
    if installed:
        return installed
    
    installed = {0:{}}
    for i in open (installed_db).readlines ()[1:]:
        name, ball, status = string.split (i)
        installed[int (status)][name] = ball
    return installed

#@+node:maphew.20100223163802.3747: *3* get_installed_version
def get_installed_version (packagename):
    return split_ball (installed[0][packagename])[1]

#@+node:maphew.20100223163802.3749: *3* get_config
def get_config(fname):
    # open /etc/setup/fname and return contents
    # e.g. /etc/setup/last-cache
    f = os.path.join(config, fname)
    if not os.path.exists(f):
        return None
    else:
        value = file(f).read().strip()
        return value

#@+node:maphew.20100307230644.3848: *3* get_menu_links
def get_menu_links(bat):
    # '''Parse postinstall batch file for menu and desktop links'''
    #
    # from 'xxmklink' lines grab first parameter, which is the link path
    # and interpret known variables.
    # Relies on shlex module which splits on spaces, yet preserves
    # spaces within quotes (http://stackoverflow.com/questions/79968)
    links = []
    for line in open(bat,'r'):
        if 'xxmklink' in line:
            link = shlex.split(line)[1]
            link = link.replace ('%OSGEO4W_ROOT%',OSGEO4W_ROOT)
            link = link.replace ('%OSGEO4W_STARTMENU%',OSGEO4W_STARTMENU)
            link = link.replace ('%ALLUSERSPROFILE%',os.environ['ALLUSERSPROFILE'])
            link = link.replace ('%USERPROFILE%',os.environ['USERPROFILE'])
            links.append(link)
    return links
#@+node:maphew.20100223163802.3751: *3* get_mirror
def get_mirror():
    if last_mirror == None:
        mirror = 'http://download.osgeo.org/osgeo4w'
    else:
        mirror = last_mirror
    return mirror

#@+node:maphew.20100223163802.3752: *3* get_missing
def get_missing (packagename):
    # print sys.argv[0], ": in get_missing with", packagename
    reqs = get_requires (packagename)
    lst = []
    for i in reqs:
        if not installed[0].has_key (i):
            lst.append (i)
    if lst and packagename not in lst:
        sys.stderr.write ('warning: missing packages: %s\n' % string.join (lst))
    elif installed[0].has_key (packagename):
        ins = get_installed_version (packagename)
        new = get_version (packagename)
        if ins >= new:
            sys.stderr.write ('%s is already the newest version\n' % packagename)
            #lst.remove (packagename)
        elif packagename not in lst:
            lst.append (packagename)
    return lst

#@+node:maphew.20100223163802.3753: *3* get_new
def get_new ():
    # '''get available upgrades '''
    global packagename
    lst = []
    for packagename in installed[0].keys ():
        new = get_version (packagename)
        ins = get_installed_version (packagename)
        if new > ins:
            debug (" %s > %s" % (new, ins))
            lst.append (packagename)
    return lst

#@+node:maphew.20100223163802.3755: *3* get_special_folder
def get_special_folder(intFolder):
    # ''' Fetch paths of Windows special folders: Program Files, Desktop, Startmenu, etc. '''
    #Written by Luke Pinner, 2010. Code is public domain, do with it what you will...
    # todo: look at replacing with WinShell module by Tim Golden,
    # http://winshell.readthedocs.org/en/latest/special-folders.html
    import ctypes
    from ctypes.wintypes import HWND , HANDLE ,DWORD ,LPCWSTR ,MAX_PATH , create_unicode_buffer
    SHGetFolderPath = ctypes.windll.shell32.SHGetFolderPathW
    SHGetFolderPath.argtypes = [HWND, ctypes.c_int, HANDLE, DWORD, LPCWSTR]
    auPathBuffer = create_unicode_buffer(MAX_PATH)
    exit_code=SHGetFolderPath(0, intFolder, 0, 0, auPathBuffer)
    return auPathBuffer.value

#@+node:maphew.20100223163802.3756: *3* get_url
def get_url (packagename):
    if not dists[distname].has_key (packagename) \
       or not dists[distname][packagename].has_key (INSTALL):
 ##       no_package ()
        # moved here from no_package(), part of remove-globals refactoring
        sys.stderr.write ("%s: %s not in [%s]\n" % ('error', packagename, distname))

        install = 0
        for d in distnames:
            if dists[d].has_key (packagename) \
               and dists[d][packagename].has_key (INSTALL):
                install = dists[d][packagename][INSTALL]
                sys.stderr.write ("warning: using [%s]\n" % d)
                break
        if not install:
            sys.stderr.write ("error: %s not installed\n" % packagename)
            sys.exit (1)
    else:
        install = dists[distname][packagename][INSTALL]
    filename, size, md5 = string.split (install)
    return filename, md5

#@+node:maphew.20100223163802.3757: *3* get_version
def get_version (packagename):
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

#@+node:maphew.20100223163802.3759: *3* get_requires
def get_requires (packagename):
    # ''' identify dependencies of package'''
    dist = dists[distname]
    if not dists[distname].has_key (packagename):
        no_package (packagename, distname)
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
#@+node:maphew.20100308085005.1381: ** Writers
#@+node:maphew.20100223163802.3750: *3* save_config
def save_config(fname,values):
    # '''save settings like last-mirror, last-cache'''
    # e.g. /etc/setup/last-cache --> d:\downloads\osgeo4w
    os.chdir(config)
    pipe = open(fname,'w')

    for i in values:
        pipe.write (i)
    if pipe.close ():
        raise TypeError('urg')
#@+node:maphew.20100223163802.3764: *3* write_installed
def write_installed ():
    ''' Record installed packages in install.db '''
    file = open (installed_db, 'w')
    file.write (installed_db_magic)
    file.writelines (map (lambda x: '%s %s 0\n' % (x, installed[0][x]),
                  installed[0].keys ()))
    if file.close ():
        raise TypeError('urg')
#@+node:maphew.20100223163802.3766: *3* write_filelist
def write_filelist (packagename, lst):
    # ''' Record installed files in package manifest (etc/setup/packagename.lst.gz) '''
    os.chdir(config)
    pipe = gzip.open (packagename + '.lst.gz','w')

    for i in lst:
        pipe.write (i)
        pipe.write ('\n')
    if pipe.close ():
        raise TypeError('urg')
#@+node:maphew.20100308085005.1382: ** Parsers
#@+node:maphew.20100223163802.3754: *3* get_setup_ini
def get_setup_ini ():
    # '''Parse setup.ini into package name, description, version, dependencies, etc.'''
    global dists
    if dists:
       # best I can figure, this is to skip redundant parsing,
       # however I don't see anywhere get_setup_ini() is
       # called more than once; candidate for removal
       print 'dists defined, skipping parse of setup.ini'
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
                raise TypeError('urg')
            if value[0] == '"' and value.find ('"', 1) == -1:
                while 1:
                    j = j + 1
                    value += lines[j]
                    if lines[j].find ('"') != -1:
                        break
            records[key] = value
            j = j + 1
        packages[name] = records
#@+node:maphew.20100223163802.3760: *3* join_ball
def join_ball (t):
    return t[0] + '-' + version_to_string (t[1])

#@+node:maphew.20100223163802.3761: *3* split_ball
def split_ball (filename):
#    ''' Parse package archive name into a) package name and b) version numbers tuple (to feed into version_to_string)
#
#    mc-4.6.0a-20030721-12.tar.bz2
#
#      mc              --> package name
#      4.6.0a-20030721 --> upstream application version
#      12              --> package version
#
#    python-numpy-2.7-1.5.1-1.tar.bz2
#
#      python-numpy  --> package name
#      2.7-1.5.1     --> upstream application version
#      1             --> package version
#
#      returns:
#
#           ('mc', (4, 6, 0a, 20030721, 12))
#           ('python-numpy', (2, 7, 1, 5, 1, 1))
#
#      '''

    ##m = re.match ('^([^.]*)-([0-9][^-/]*-[0-9][0-9]*)(.tar.bz2)?$', filename)    # original regex from cyg-apt
    ##m = re.match ('^([^.]*)-([0-9].*-[0-9][0-9]*)(.tar.bz2)?$', filename)        # accept dash in app ver num

    # this regex pattern should be functionally identical to the line immediately above
    regex = re.compile('''
       ^       	    # beginning of line
       ([^.]*) 	    # package name: any char except period, and any amount of them, "python-numpy"
       -                # name/version delimiter
       (
           [0-9].*    # application version: any number followed by any char, any amount of them, "4.6.0a-20030721"
           -[0-9]*    # package version: dash followed by number, "-12"
           )
       .*               # accept any trailing chars after the package version
       (\.tar\.bz2)?$
       ''', re.VERBOSE)

    m = re.match(regex, filename)
    if not m:
        print '\n\n*** Error parsing version number from "%s"\n%s\n' % (filename, m)
    return (m.group(1), string_to_version(m.group (2)))
#@+node:maphew.20100223163802.3762: *3* string_to_version
def string_to_version (s):
    # bash-2.05b-9
    # return map (string.atoi, (string.split (re.sub ('[.-]', ' ', s))))
    s = re.sub ('([^0-9][^0-9]*)', ' \\1 ', s)
    s = re.sub ('[ .-][ .-]*', ' ', s)
    def try_atoi (x):
        if re.match ('^[0-9]*$', x):
            return string.atoi (x)
        return x
    return tuple (map (try_atoi, (string.split (s))))

#@+node:maphew.20100223163802.3763: *3* version_to_string
def version_to_string (t):
    #return '%s-%s' % (string.join (map (lambda x: "%d" % x, t[:-1]), '.'),
    #         t[-1])
    def try_itoa (x):
        if type (x) == int:
            return "%d" % x
        return x
    return '%s-%s' % (string.join (map (try_itoa, t[:-1]), '.'),
              t[-1])

#@+node:maphew.20100223163802.3758: ** no_package
def no_package (packagename, distname, s='error'):
    sys.stderr.write ("Warning: %s not in distribution [%s]\n" % (packagename, distname))

#@+node:maphew.20100302221232.1486: ** psort (disabled)
#def psort (lst): #Raises "AttributeError: 'function' object has no attribute 'sort'" use sorted() instead
#    plist.sort (lst)
#    return lst
#@+node:maphew.20100223163802.3765: ** post_install
def post_install (packagename):
    # ''' Run postinstall batch files and update package manifest
    #     to catch those files not included in the package archive.
    #     (manifest = etc/setup/pkg-foo.lst.gz) '''
    # adapted from "17.1.3.3 Replacing os.system()"
    # http://www.python.org/doc/2.5.2/lib/node536.html

    os.chdir(root)

    # necessary for textreplace, xxmklink
    os.putenv('PATH', '%s\\bin' % os.path.normpath(OSGEO4W_ROOT))

    for bat in glob.glob ('%s/etc/postinstall/*.bat' % root):
        try:
            # run the postinstall batch files
            retcode = subprocess.call (bat, shell=True)
            if retcode < 0:
                print >>sys.stderr, "Child was terminated by signal", -retcode

            # then update manifest
            else:
                # mark bat as completed
                done_bat = bat + '.done'
                if os.path.exists(done_bat):
                    os.remove(done_bat)
                os.rename(bat, done_bat)

                # harmonize path conventions
                # TODO: Move/merge this to cyg_path helper function
                bat = bat.replace (root, '')         # strip C:\osgeo4w
                bat = bat.replace ('\\','/')         # backslash to foreslash
                bat = bat.replace ('/etc/', 'etc/')  # strip leading slash

                # foo.bat --> foo.bat.done in manifest
                lst = get_filelist(packagename)

                # ticket #281, ignore leading dot slash in filenames (./foo.bat --> foo.bat)
                lst = [x.replace('./','') for x in lst]

                if bat in lst:
                    lst.remove(bat)
                    lst.append(bat + '.done')
                else:
                    print """\nwarning: adding %s to install manifest failed.
                    It will need to be removed manually when uninstalling or upgrading this package""" % done_bat

                # retrieve menu & desktop links from postinstall bats
                for link in get_menu_links(done_bat):
                    lst.append(link)

                for s in lst:
                    # bin/bar.bat.tmpl --> both bin/bar.bat and bin/bar.bat.tmpl in manifest
                    if s.endswith('.tmpl'):
                         lst.append(s.replace('.tmpl',''))
                    # catch bat's which are made for py's post install
                    if s.startswith('bin/') and s.endswith('.py'):
                        p =  re.compile(r'^bin/(.*?)\.py$', re.VERBOSE)
                        out = p.sub(r'bin/\1.bat', s)
                        lst.append(out)

                write_filelist (packagename, lst)

                print >>sys.stderr, "Post_install complete, return code", retcode

        except OSError, e:
            print >>sys.stderr, "Execution failed:", e
#@+node:maphew.20100223163802.3771: ** Building from source
#@+node:maphew.20100223163802.3767: *3* do_unpack

###########################
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
        raise TypeError('urg1')
    print ('%s/%s' % (SRC, packagename))
    if not os.path.exists ('%s/%s' % (SRC, packagename)):
        raise TypeError('urg2')        

#@+node:maphew.20100223163802.3768: *3* do_build
def do_build ():
    src = '%s/%s' % (SRC, packagename)
    if not os.path.exists (src):
        raise TypeError('urg')
        
    m = re.match ('^(.*)-([0-9]*)$', packagename)
    if not m:
        raise TypeError('urg')
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

#@+node:maphew.20100223163802.3769: *3* build
def build ():
    # commented docstring hides this unused function from usage message
    # '''build package from source in CWD'''
    global packagename
    if not packagename:
        packagename = os.path.basename (CWD)
    do_build ()

#@+node:maphew.20100223163802.3770: *3* source
def source ():
    # commented docstring hides this unused function from usage message
    # '''download, build and install'''
    global packagename
    # let's not do dependencies
    #for packagename in missing.keys ():
    global INSTALL
    INSTALL = 'source'
    for packagename in packages:
        download ()
    for packagename in packages:
        do_unpack ()
        do_build ()
    if 1 or download_p:
        sys.exit (0)


#@-others
###########################
#Main
###########################
if __name__ == '__main__':

    #@+<<globals>>
    #@+node:maphew.20100307230644.3841: ** <<globals>>
    OSGEO4W_ROOT = check_env() # verify OSGEO4W_ROOT is set
        
    CWD = os.getcwd ()
    INSTALL = 'install'
    installed = 0

    root = OSGEO4W_ROOT
    config = root + '/etc/setup/'
    setup_ini = config + '/setup.ini'
    setup_bak = config + '/setup.bak'
    installed_db = config + '/installed.db'
    installed_db_magic = 'INSTALLED.DB 2\n'
    #@-<<globals>>
    #@+<<parse command line>>
    #@+node:maphew.20100307230644.3842: ** <<parse command line>>
    # FIXME: 'files' for a var name here is a misnomer, as the 1st element is actually
    # the command (install, remove, etc.), consequently everywhere the list of package
    # names from cmdline is needed the cumbersome `files[1:]` is used.
    #
    (options, params) = getopt.getopt (sys.argv[1:],
                      'dhi:m:r:t:s:x',
                      ('download', 'help', 'mirror=', 'root='
                       'ini=', 't=', 'start-menu=', 'no-deps'))

    # we start with assumption help is the action to take,
    # and switch to something else only if instructed so
    command = 'help'

    # the first parameter is our action
    if len (params) > 0:
        command = params[0]

    # and all following are package names
    packages = params[1:]

    ##packagename = 0
    ##if packages:
    ##    packagename = packages[0]
    # if len (params) > 1:
        # packagename = params[1]


    distname = 'curr'

    depend_p = 0
    download_p = 0
    start_menu_name = 'OSGeo4W'
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
          # use either local or url file for setup.ini, was:
          # setup_ini = a
          setup_ini = urllib.urlretrieve(a)
          setup_ini = setup_ini[0]
        elif o == '--mirror' or o == '-m':
            mirror = a
        elif o == '--root' or o == '-r':
            root = a
        elif o == '--t' or o == '-t':
            distname = a
        elif o == '--no-deps' or o == '-x':
            depend_p = 1
        elif o == '--start-menu' or o == '-s':
            start_menu_name = a

    # Thank you Luke Pinner for answering how to get path of "Start > Programs"
    # http://stackoverflow.com/questions/2216173
    #PROGRAMS=2
    ALLUSERSPROGRAMS=23
    OSGEO4W_STARTMENU = get_special_folder(ALLUSERSPROGRAMS) + "\\" + start_menu_name
    os.putenv('OSGEO4W_STARTMENU', OSGEO4W_STARTMENU)

    dists = 0
    distnames = ('curr', 'test', 'prev')
    #@-<<parse command line>>
    #@+<<post-parse globals>>
    #@+node:maphew.20100307230644.3844: ** <<post-parse globals>>
    last_mirror = get_config('last-mirror')
    last_cache = get_config('last-cache')

    if not 'mirror' in globals():
        mirror = get_mirror()

    # convert mirror url into acceptable folder name
    mirror_dir = urllib.quote (mirror, '').lower ()

    if last_cache == None:
        cache_dir = '%s/var/cache/setup' % (root)
    else:
        cache_dir = last_cache

    downloads = '%s/%s' % (cache_dir, mirror_dir)

    ##fixme: this is useful, but too noisy to report every time
    #print "Last cache:\t%s\nLast mirror:\t%s" % (last_cache, last_mirror)
    #print "Using mirror:\t%s" % (mirror)
    #print "Saving to:\t%s" % (cache_dir)
    #@-<<post-parse globals>>
    #@+<<run the commands>>
    #@+node:maphew.20100307230644.3843: ** <<run the commands>>
    if command == 'setup':
        setup ()
        sys.exit (0)

    elif command == 'update':
        update ()
        sys.exit (0)

    elif command == 'help':
        help ()

    else:
        check_setup(installed_db, setup_ini)

        get_setup_ini ()
        get_installed ()

        if command and command in __main__.__dict__:
            __main__.__dict__[command] (packages)
        else:
            print '"%s" not understood, please run "apt help"' % command
    #@-<<run the commands>>
    #@+<<wrap up>>
    #@+node:maphew.20100307230644.3845: ** <<wrap up>>
    save_config('last-mirror', mirror)
    save_config('last-cache', cache_dir)
    #@-<<wrap up>>
#@-leo
