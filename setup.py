#!/usr/bin/env python

import os
import sys

try:
    from setuptools import setup, Command
except ImportError:
    from distutils.core import setup, Command


if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist upload')
    sys.exit()


readme = open('README.rst').read()
doclink = """
Documentation
-------------

The full documentation is at http://drf-json-api.rtfd.org."""
history = open('HISTORY.rst').read().replace('.. :changelog:', '')

setup(
    name='drf-json-api',
    version='0.1.0',
    description=(
        'A parser and renderer for Django REST Framework that adds support'
        ' for the JSON API specification.'),
    long_description=readme + '\n\n' + doclink + '\n\n' + history,
    author='Kevin Brown',
    author_email='kevin@kevinbrown.in',
    url='https://github.com/kevin-brown/drf-json-api',
    packages=[
        'rest_framework_json_api',
    ],
    package_dir={'rest_framework_json_api': 'rest_framework_json_api'},
    include_package_data=True,
    install_requires=[
    ],
    license='MIT',
    zip_safe=False,
    keywords='drf-json-api',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: Implementation :: PyPy',
    ],
)
