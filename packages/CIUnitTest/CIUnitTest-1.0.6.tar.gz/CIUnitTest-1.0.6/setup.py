#!/usr/bin/python
# -*- coding: utf8 -*-

from distutils.core import setup

setup(name='CIUnitTest',
      version='1.0.6',
      description='Provides test results of unittest in JSON format, in '
                  'order to be able to use the results programmatically.',
      long_description=open('README.rst').read(),
      author='Arseni Mourzenko',
      author_email='arseni.mourzenko@pelicandd.com',
      url='http://go.pelicandd.com/n/python-ciunittest',
      license='MS-PL',
      keywords='unittest ci continuous-integration json',
      py_modules=['ciunittest'])
