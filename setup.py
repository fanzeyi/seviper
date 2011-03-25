#!/usr/bin/env python

from distutils.core import setup

setup(name='seviper',
      version='0.1', # UPDATE bin/fanfou too
      description='A command-line client of Fanfou, a Chinese microblog.',
      license='GNU Ceneral Public License (GPL)',
      url='https://github.com/upsuper/seviper',
      packages=['fanfou'],
      py_modules=['termcolor'],
      scripts=['bin/fanfou', 'bin/fanfou-gui'],
      )
