#!/usr/bin/env python

from distutils.core import setup

version = open('VERSION', 'r').read().strip()

setup(name='ModestMaps',
      version=version,
      description='Modest Maps python port',
      author='Michal Migurski',
      url='http://modestmaps.com',
      requires=['PIL'],
      packages=['ModestMaps'],
      license='BSD')
