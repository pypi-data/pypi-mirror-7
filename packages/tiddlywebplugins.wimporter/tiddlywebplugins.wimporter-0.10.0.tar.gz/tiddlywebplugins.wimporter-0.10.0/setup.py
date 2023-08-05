
import os
from setuptools import setup, find_packages

VERSION = '0.10.0'

setup(
        namespace_packages = ['tiddlywebplugins'],
        name = 'tiddlywebplugins.wimporter',
        version = VERSION,
        description = 'A TiddlyWeb plugin for server side import of tiddlers.',
        long_description=file(os.path.join(os.path.dirname(__file__), 'README')).read(),
        author = 'Chris Dent',
        url = 'http://pypi.python.org/pypi/tiddlywebplugins.wimporter',
        packages = find_packages(exclude=['test']),
        author_email = 'cdent@peermore.com',
        platforms = 'Posix; MacOS X; Windows',
        install_requires = ['setuptools',
            'tiddlyweb>=2.1.2',
            'tiddlywebplugins.twimport>=0.9',
            'httpexceptor',
            'tiddlywebplugins.utils',
            'tiddlywebplugins.templates'],
        include_package_data = True,
        zip_safe=False
        )

