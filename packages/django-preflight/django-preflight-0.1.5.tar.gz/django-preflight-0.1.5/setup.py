# -*- encoding: utf-8 -*-
# Copyright 2010 Canonical Ltd.  This software is licensed under the
# GNU Affero General Public License version 3 (see the file LICENSE).
import sys

try:
    from ast import PyCF_ONLY_AST
except ImportError:
    PyCF_ONLY_AST = 1024

from setuptools import setup


def get_version():
    return [compile(line, '', 'exec', PyCF_ONLY_AST).body[0].value.s
            for line in open('preflight/__init__.py')
            if line.startswith('__version__')][0]

tests_require = [
    'mock > 0.6',
    'gargoyle >= 0.6.0',
    'pyquery',
]

if sys.version_info[:2] < (2, 7):
    tests_require.append('unittest2')

setup(
    name='django-preflight',
    version=get_version(),
    author='Lukasz Czyzykowski',
    author_email='lukasz.czyzykowski@canonical.com',
    description="Create a page for making sure all settings are correct.",
    long_description=open('README').read(),
    url='https://launchpad.net/django-preflight',
    download_url='https://launchpad.net/django-preflight/+download',
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Web Environment",
        "Framework :: Django",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU Affero General Public License v3",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Topic :: Internet :: WWW/HTTP :: Site Management",
        "Topic :: Software Development :: Quality Assurance",
    ],
    license='AGPL-3',
    packages=(
        'preflight',
        'preflight.management',
        'preflight.management.commands',
    ),
    package_data={
        'preflight': ['templates/preflight/*.html'],
    },
    install_requires=[
        'django >= 1.4',
    ],
    tests_require=tests_require,
    extras_require={
        'docs': ['Sphinx'],
    },
    test_suite='preflight_example_project.run.tests',
)
