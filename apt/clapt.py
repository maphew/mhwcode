''' Click experiments with apt
'''

import click
import os
import sys

#Configuration values which are used by all functions.
#current form is ugly, hard to read, but works.
# a simple ini like form is better for reading, but I don't know how to
# code for clarity here.
#       root = 'c:/osgeo4w'
#       etc_setup = 'c:/osgeo4w/etc/setup'
#       setup_ini = 'c:/osgeo4w/etc/setup/setup.ini'
#       ...
config = {}
config['root'] = 'OSGEO4W_ROOT'
config['etc_setup'] = config['root'] + '/etc/setup/'
config['setup_ini'] = config['etc_setup'] + '/setup.ini'
config['setup_bak'] = config['etc_setup'] + '/setup.bak'
config['installed_db'] = config['etc_setup'] + '/installed.db'
config['installed_db_magic'] = 'INSTALLED.DB 2\n'

CONFIG_SETTINGS = dict(
    default_map={'setup':config}
)


@click.group(context_settings=CONFIG_SETTINGS)
@click.pass_context
def cli(ctx):
    pass

@cli.command()
@click.pass_context
@click.argument('root')
def setup(root):
    click.echo('setting up new o4w skeleton in: %s' % root)
    os.putenv('OSGEO4W_ROOT', root)
    if os.path.exists(root):
        sys.exit('abort: "%s" already exists' % root)
    click.echo('Creating root folder')
    os.mkdir(root)
    click.echo('Creating %s\n' % config['etc_setup'])
    os.makedirs(config['etc_setup'])
    click.echo('Creating %s\n' % config['installed_db'])
    installed = {0:{}}
##    write_installed(installed)
    click.echo('getting %s\n' % config['setup_ini'])
##    update ()


@cli.command()
@click.pass_context
@click.argument('packages', nargs=-1, required=True)
def install(packages):
    for pkg in packages:
        click.echo('Installing: %s' % pkg)

@cli.command()
@click.pass_context
@click.argument('packages', nargs=-1, required=True)
def remove(packages):
    for pkg in packages:
        click.echo('Removing: %s' % pkg)




##def setup(config, mirror):
##    '''Create on OSGEO4W skeleton environment (folder tree &
##    installed packages database'''
##    click.echo('Creating system skeleton in: %s' % folder)
##    click.echo('Package repository (mirror): %s' % mirror)
##    click.echo('root folder: %s' % config.root)

##@click.option('--root', envvar='OSGEO4W_ROOT',
##    default=r'C:\OSGeo4W',
##    type=click.Path())
##
##
##@cli.command()
##@click.option('--mirror')
##@click.pass_obj
##@click.option('--mirror',
##    default='http://download.osgeo.org/osgeo4w/x86/release',
##    help='specify url of package repository')



if __name__ == '__main__':
    cli()
