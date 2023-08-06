#!/usr/bin/python
# -*- coding: utf-8 -*-

# This file is part of avos.
# https://github.com/wumaogit/avos

# Licensed under the MIT license:
# http://www.opensource.org/licenses/MIT-license
# Copyright (c) 2014 wumaogit actor2019@gmail.com

from __future__ import absolute_import
from setuptools import setup, find_packages
from avos.version import __version__

tests_require = [
    'mock',
    'nose',
    'coverage',
    'yanc',
    'preggy',
    'tox',
    'ipdb',
    'coveralls',
    'sphinx',
]

setup(
    name='avos',
    version=__version__,
    description='an incredible python package',
    long_description='''
an incredible python package
''',
    keywords='avos avoscloud ',
    author='wumaogit',
    author_email='actor2019@gmail.com',
    url='https://github.com/wumaogit/avos',
    license='MIT',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: Unix',
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: Implementation :: PyPy",
        'Operating System :: OS Independent',
    ],
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        # add your dependencies here
        # remember to use 'package-name>=x.y.z,<x.y+1.0' notation (this way you get bugfixes)
        'requests',
        'arrow'
    ],
    extras_require={
        'tests': tests_require,
    },
    entry_points={
        'console_scripts': [
            # add cli scripts here in this form:
            # 'avos=avos.cli:main',
        ],
    },
)
