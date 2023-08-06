import sys

from setuptools import setup

import versioneer


versioneer.versionfile_source = 'doto/_version.py'
versioneer.versionfile_build = 'doto/_version.py'
versioneer.tag_prefix = ''
versioneer.parentdir_prefix = 'doto-'

setup(
    name = 'doto',
    version = versioneer.get_version(),
    cmdclass = versioneer.get_cmdclass(),
    description='Python Interface to Digital Ocean',
    author = 'Benjamin Zaitlen',
    packages = ['doto','doto.commands'],
    install_requires=['requests>=2.0.1',
                      'pycrypto>=2.6.1'],
    package_data={'doto':['dotorc']},
    entry_points = {
        'console_scripts' : [
            'doto = doto.cli:main'
            ]
    }

)