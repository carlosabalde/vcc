#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Varnish Custom Counters
=======================

Varnish Custom Counters (VCC) allows aggregation of custom log entries
extracted from Varnish shared memory log.

Check out https://github.com/carlosabalde/vcc for a detailed description,
extra documentation and other useful information.

:copyright: (c) 2014 by Carlos Abalde, see AUTHORS.txt for more details.
:license: BSD, see LICENSE.txt for more details.
'''

from __future__ import absolute_import
import os
import sys
from setuptools import setup, find_packages

if sys.version_info < (2, 6) or sys.version_info[0] > 2:
    raise Exception('Varnish Custom Counters requires Python >= 2.6 and < 3.')

with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'requirements.txt')) as file:
    install_requires = file.read().splitlines()

setup(
    name='VCC',
    version=0.1,
    author='Carlos Abalde',
    author_email='carlos.abalde@gmail.com',
    packages=find_packages(),
    include_package_data=True,
    url='https://github.com/carlosabalde/vcc',
    description=
        'Varnish Custom Counters (VCC) allows aggregation of custom log entries '
        'extracted from Varnish shared memory log.',
    long_description=__doc__,
    license='GPL',
    entry_points={
        'console_scripts': [
            'vcc = vcc.runner:main',
        ],
    },
    classifiers=[
        'Intended Audience :: System Administrators',
        'Operating System :: OS Independent',
    ],
    install_requires=install_requires
)
