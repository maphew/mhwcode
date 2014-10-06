from setuptools import setup

setup(
    name='AptInstaller',
    version='0.3',
    py_modules=['apt','dapt'],
    install_requires=['Click'],
    entry_points='''
        [console_scripts]
        apt = apt:main
        dapt = dapt:main
        '''
    )
