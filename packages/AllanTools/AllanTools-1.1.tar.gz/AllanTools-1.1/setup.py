#!/usr/bin/env python

from distutils.core import setup

setup(name='AllanTools',
      version='1.1',
      description='Allan deviation and related time/frequency statistics',
      author='Anders Wallin',
      author_email='anders.e.e.wallin@gmail.com',
      url='https://github.com/aewallin/allantools',
      license='GPLv3+',
      packages=['allantools',],
      requires=['numpy'],
      long_description="""Given phase or fractional frequency data this package calculates:
                        Allan deviation, overlapping Allan deviation, modified Allan deviation
                        Hadamard deviation, overlapping Hadamard deviation, time deviation,
                        total deviation, MTIE, TIE-rms"""
     )
