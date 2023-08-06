# -*- coding: utf-8 -*-
from setuptools import setup

from chopper import __version__


with open('README.rst', 'r') as f:
    long_description = f.read()

setup(
    name='chopper',
    version=__version__,
    description="Lib to extract html elements by preserving ancestors and cleaning CSS",
    long_description=long_description,
    author=u'Jurismarchés',
    author_email='contact@jurismarches.com',
    url='https://github.com/jurismarches/chopper',
    packages=[
        'chopper',
        'chopper.css',
        'chopper.html',
    ],
    install_requires=[
        'cssselect==0.9.1',
        'tinycss==0.3',
        'lxml==3.3.5',
        'six==1.7.3'
    ],
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.1',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4'
    ],
    test_suite='chopper.tests'
)
