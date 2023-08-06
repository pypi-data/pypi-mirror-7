#!/usr/bin/env python
# coding: utf-8
import sys
from setuptools import setup


setup(
    name='rlog',
    version='0.0.2',
    description='Small handler and formatter for using python logging with Redis',
    url='https://github.com/lobziik/rlog',
    tests_require=['pytest>=2.5.0', 'mock'],
    install_requires=['redis', 'ujson'],
    packages=['rlog', 'tests'],
    license='MIT',
    keywords=['Redis', 'logging', 'log', 'logs'],
    author="lobziik",
    author_email="lobziiko.o@gmail.com",
    maintainer="lobziik",
    maintainer_email="lobziiko.o@gmail.com",
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4'
    ]
)
