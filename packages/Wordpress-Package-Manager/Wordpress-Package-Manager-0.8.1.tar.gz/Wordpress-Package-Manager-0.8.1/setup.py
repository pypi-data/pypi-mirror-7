#!/usr/bin/env python
from distutils.core import setup
from distutils.command.install_data import install_data

setup(name='Wordpress-Package-Manager',
      version='0.8.1',
      description='A command-line tool for installing WordPress plugins',
      long_description="A command-line tool for installing WordPress plugins in a manner similar to PIP.",
      author='Ryan Bagwell',
      author_email='ryan@ryanbagwell.com',
      url='https://github.com/ryanbagwell',
      scripts=['bin/wpm'],
     )