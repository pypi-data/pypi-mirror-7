#!/usr/bin/env
# -*- coding: utf-8 -*-
# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4
# Author: "Chris Ward <cward@redhat.com>

from setuptools import setup

VERSION_FILE = "tornadohttp/_version.py"
VERSION_EXEC = ''.join(open(VERSION_FILE).readlines())
__version__ = ''
exec(VERSION_EXEC)  # update __version__
if not __version__:
    raise RuntimeError("Unable to find version string in %s." % VERSION_FILE)

__pkg__ = 'tornadohttp'
__pkgs__ = ['tornadohttp']
__provides__ = ['tornadohttp']
__desc__ = 'Generic Tornado Server'
__scripts__ = []
__requires__ = [
    'tornado (>=3.2)',
]
__irequires__ = [
    'tornado>=3.2',
]
pip_src = 'https://pypi.python.org/packages/source'
__deplinks__ = []

with open('README.rst') as _file:
    readme = _file.read()

github = 'https://github.com/kejbaly2/tornadohttp'
download_url = '%s/archive/master.zip' % github

default_setup = dict(
    url=github,
    license='GPLv3',
    author='Chris Ward',
    author_email='cward@redhat.com',
    download_url=download_url,
    long_description=readme,
    data_files=[],
    classifiers=[
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Natural Language :: English',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 2 :: Only',
        'Topic :: Utilities',
    ],
    keywords=['tornado'],
    dependency_links=__deplinks__,
    description=__desc__,
    install_requires=__irequires__,
    name=__pkg__,
    packages=__pkgs__,
    provides=__provides__,
    requires=__requires__,
    scripts=__scripts__,
    version=__version__,
)

setup(**default_setup)
