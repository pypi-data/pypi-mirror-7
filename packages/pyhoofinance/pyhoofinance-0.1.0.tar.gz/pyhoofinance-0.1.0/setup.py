#!/usr/bin/env python
#
#  pyhoofinance - setup.py
#
#  Copyright (c) 2014, Rob Innes Hislop
#  email:robinneshislop__AT__gmail.com
#
# This library is distributed under the terms of the 
# GNU General Public License (or the Lesser GPL)
# version 3.
   
from setuptools import setup, find_packages

__version__ = '0.1.0'
setup(
    name='pyhoofinance',
    version=__version__,
    author='Rob Innes Hislop',
    author_email='robinneshislop@gmail.com',
    packages=find_packages(),
    license='GNU LGPL License',
    description='Set of functions for retreiving equity data from Yahoo finance',
    long_description='This module queries Yahoo Finance for multiple tickers and rapidly return typed data. It will also retrieve historic information, formatted into the proper data type. It is designed for performing analysis quickly with large numbers of symbols.'
)