#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

# for uploading to pypi
if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist upload')
    sys.exit()

requires = open("requirements.txt").readlines()

setup(
    name="brlcad",
    version="0.0.0",
    description="python bindings for BRLCAD (cython)",
    long_description=open("README.md", "r").read(),
    license="BSD",
    author="Bryan Bishop",
    author_email="kanzure@gmail.com",
    url="https://github.com/kanzure/python-brlcad",
    packages=["brlcad"],
    package_dir={"brlcad": "brlcad"},
    include_package_data=True,
    install_requires=requires,
    platforms="any",
    classifiers=[
        "License :: OSI Approved :: BSD License",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
    ],
)
