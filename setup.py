# -*- coding: utf-8 -*-
#
# you can install this to a local test virtualenv like so:
#   virtualenv venv
#   ./venv/bin/pip install --editable .
#   ./venv/bin/pip install --editable .[dev]  # with dev requirements, too

from __future__ import print_function

import os.path
import subprocess
import sys
from io import open

from setuptools import setup

from coursera_helper import __version__


def generate_readme_rst():
    """
    Generate README.rst from README.md via pandoc.

    In case of errors, we show a message having the error that we got and
    exit the program.
    """

    pandoc_cmd = [
        'pandoc',
        '--from=markdown',
        '--to=rst',
        '--output=README.rst',
        'README.md'
    ]

    if os.path.exists('README.rst'):
        return
    try:
        subprocess.call(pandoc_cmd)
    except (IOError, OSError) as e:
        print('Could not run "pandoc". Error: %s' % e, file=sys.stderr)
        print('Generating only a stub instead of the real documentation.')


def read_file(filename, alt=None):
    """
    Read the contents of filename or give an alternative result instead.
    """
    try:
        with open(filename, encoding='utf-8') as f:
            return f.read()
    except IOError:
        return [] if alt is None else alt


generate_readme_rst()

long_description = read_file(
    'README.md',
    'Cannot read README.md'
)
requirements = read_file('requirements.txt')
dev_requirements = read_file('requirements-dev.txt')

trove_classifiers = [
    'Development Status :: 4 - Beta',
    'Environment :: Console',
    'Intended Audience :: End Users/Desktop',
    'License :: OSI Approved :: GNU Lesser General Public License v3 or later (LGPLv3+)',
    'Operating System :: OS Independent',
    'Programming Language :: Python',
    'Programming Language :: Python :: 3.8',
    'Programming Language :: Python :: 3.9',
    'Programming Language :: Python :: 3.10',
    'Programming Language :: Python :: 3.11',
    'Programming Language :: Python :: Implementation :: CPython',
    'Programming Language :: Python :: Implementation :: PyPy',
    'Topic :: Education',
]

setup(
    name='coursera-helper',
    version=__version__,
    maintainer='Spiros Keverkloglou',
    maintainer_email='spiros.kraz@hotmail.com',

    license='LGPL',
    url='https://github.com/krazator/coursera-helper',

    install_requires=requirements,
    extras_require=dict(
        dev=dev_requirements
    ),

    description='Script for downloading Coursera.org videos and naming them.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    keywords=['coursera-helper', 'coursera',
              'download', 'education', 'MOOCs', 'video'],
    classifiers=trove_classifiers,

    packages=["coursera_helper"],
    entry_points=dict(
        console_scripts=[
            'coursera-helper=coursera_helper.coursera_dl:main'
        ]
    ),

    platforms=['any'],
)
