#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from setuptools import setup

README = open(os.path.join(os.path.dirname(__file__), 'README.md')).read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='django-hooks',
    version='0.1.0',
    description='A plugin system for django.',
    author='Esteban Castro Borsani',
    author_email='ecastroborsani@gmail.com',
    long_description=README,
    url='https://github.com/nitely/django-hooks',
    packages=[
        'hooks',
    ],
    include_package_data=True,
    zip_safe=False,
    license='MIT License',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
)
