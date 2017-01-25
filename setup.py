#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = [
    'numpy>=1.9',
    'scipy>=0.15',
    'Cython>=0.25.2',
    'javabridge==1.0.15',
    'python-bioformats>=1.0.8'
]

test_requirements = [
    # TODO: put package test requirements here
    'nose>=1.3',
    'numpy>=1.9',
    'scipy>=0.15',
    'Cython>=0.25.2',
    'javabridge==1.0.15',
    'python-bioformats>=1.0.8'
]

setup(
    name='pyome',
    version='0.1.0',
    description="Python library for reading and interacting with OME image metadata",
    long_description=readme + '\n\n' + history,
    author="Keith Schulze",
    author_email='keith.schulze@monash.edu',
    url='https://github.com/keithschulze/pyome',
    packages=[
        'pyome',
    ],
    package_dir={'pyome':
                 'pyome'},
    include_package_data=True,
    install_requires=requirements,
    dependency_links=[
        'https://github.com/LeeKamentsky/python-javabridge/archive/master.zip#egg=javabridge-1.0.15'
    ],
    license="MIT",
    zip_safe=False,
    keywords='pyome',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    test_suite='tests',
    tests_require=test_requirements,
)
