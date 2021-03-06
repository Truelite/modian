#!/usr/bin/env python3

# live-wrapper - Wrapper for vmdebootstrap to create live images
# (C) Iain R. Learmonth 2015 <irl@debian.org>
# See COPYING for terms of usage, modification and redistribution.
# 
# setup.py - setuptools script

from setuptools import setup, find_packages
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'VERSION')) as version_file:
    version = version_file.read().strip()

setup(
    name='modian-live-wrapper',
    version=version,
    description='Create a Debian live image',
    author='Enrico Zini',
    author_email='enrico@debian.org',
    url='',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.5',
        'Topic :: System :: Installation/Setup',
    ],
    packages=[
        'lwr',
    ],
    package_data={
        'live-wrapper': ['README.md', 'COPYING'],
    },
    install_requires=[
        'requests',
        'pycurl',
        'python-apt'
    ],
    entry_points={
        'console_scripts': [
            'modian-lwr = lwr.run:main',
        ],
    },
)
