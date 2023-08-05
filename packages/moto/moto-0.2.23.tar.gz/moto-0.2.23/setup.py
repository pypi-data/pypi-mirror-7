#!/usr/bin/env python

from setuptools import setup, find_packages

install_requires = [
    "boto",
    "dicttoxml",
    "flask",
    "httpretty>=0.6.1",
    "Jinja2",
    "xmltodict",
]

import sys

if sys.version_info < (2, 7):
    # No buildint OrderedDict before 2.7
    install_requires.append('ordereddict')

setup(
    name='moto',
    version='0.2.23',
    description='A library that allows your python tests to easily'
                ' mock out the boto library',
    author='Steve Pulec',
    author_email='spulec@gmail',
    url='https://github.com/spulec/moto',
    entry_points={
        'console_scripts': [
            'moto_server = moto.server:main',
        ],
    },
    packages=find_packages(exclude=("tests", "tests.*")),
    install_requires=install_requires,
)
