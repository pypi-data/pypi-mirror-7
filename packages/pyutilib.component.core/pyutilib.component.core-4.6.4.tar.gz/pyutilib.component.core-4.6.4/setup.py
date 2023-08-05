#  _________________________________________________________________________
#
#  PyUtilib: A Python utility library.
#  Copyright (c) 2008 Sandia Corporation.
#  This software is distributed under the BSD License.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  _________________________________________________________________________

"""
Setup for pyutilib.component.core package
"""

import sys
import os
from setuptools import setup
from os.path import dirname, realpath, abspath, join
import shutil

if os.path.exists('../README.txt'):
    shutil.copy('../README.txt', '.')

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()


setup(name="pyutilib.component.core",
    version='4.6.4',
    maintainer='William E. Hart',
    maintainer_email='wehart@sandia.gov',
    url = 'https://software.sandia.gov/svn/public/pyutilib/pyutilib.component.core',
    license = 'BSD',
    platforms = ["any"],
    description = 'The PyUtilib Component Architecture.',
    long_description = read('README.txt'),
    classifiers = [
        'Development Status :: 4 - Beta',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: Unix',
        'Programming Language :: Python',
        'Programming Language :: Unix Shell',
        'Topic :: Scientific/Engineering :: Mathematics',
        'Topic :: Software Development :: Libraries :: Python Modules'],
      packages=['pyutilib', 'pyutilib.component', 'pyutilib.component.core'],
      install_requires=['six'],
      keywords=['utility'],
      namespace_packages=['pyutilib', 'pyutilib.component']
      )
