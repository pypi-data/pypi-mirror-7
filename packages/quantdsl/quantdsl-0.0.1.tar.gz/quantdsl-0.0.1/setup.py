#!/usr/bin/env python
import os
import sys
from setuptools import setup
from quantdsl import __version__

long_description = open('README').read()

setup(
    name='quantdsl',
    version=__version__,

    packages=['quantdsl'],
    # just use auto-include and specify special items in MANIFEST.in
    zip_safe = False,
    install_requires = [
        'scipy',
        'numpy',
    ],
    author='Appropriate Software Foundation',
    author_email='quant-support@appropriatesoftware.net',
    license='MIT',
    url='http://appropriatesoftware.net/quant',
    description='Domain specific language for quantitative analytics in finance.',
    long_description = long_description,
    # Todo: Review these classifiers.
    classifiers = [
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: Education',
        'Intended Audience :: Financial and Insurance Industry',
        'Intended Audience :: Science/Research',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Office/Business :: Financial',
        'Topic :: Office/Business :: Financial :: Investment',
        'Topic :: Office/Business :: Financial :: Spreadsheet',
        'Topic :: Scientific/Engineering :: Information Analysis',
        'Topic :: Scientific/Engineering :: Mathematics',
        'Topic :: Software Development :: Libraries :: Python Modules',
   ],
)
