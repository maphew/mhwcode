''' Working with Click, adapting example of git-like complex application
    to apt.
'''
import os
import click

class Config(object):
    def __init__(self, root=None):
        self.root = r'b:\o4w-xxx'

pass_config = click.make_pass_decorator(Config)

@click.group()
@click.option('--root', envvar='OSGEO4W_ROOT', default=r'B:\o4w-default')
@click.pass_context
def cli(ctx, root):
    ctx.obj = Config(root)


@cli.command()
@click.argument('dest', required=True)
@pass_config
def setup(config, dest):
    click.echo('setting up new o4w skeleton in: %s' % config.root)

if __name__ == '__main__':
    cli()
