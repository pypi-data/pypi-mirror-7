#!/usr/bin/env python

from distutils.core import setup

setup(name='datapoint',
      version='0.1',
      install_requires=[
          "requests >= 2.3.0",
      ],
      description='Python interface to the Met Office\'s Datapoint API',
      author='Jacob Tomlinson',
      author_email='jacob@jacobtomlinson.co.uk',
      url='',
      packages=['datapoint'],
     )
