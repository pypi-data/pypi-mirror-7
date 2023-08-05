#!/usr/bin/env python
from distutils.core import setup
from distutils.command.install_data import install_data
from cx_Freeze import setup, Executable

setup(name='Wordpress-Package-Manager',
      version='0.8.2',
      description='A command-line tool for installing WordPress plugins',
      long_description="A command-line tool for installing WordPress plugins in a manner similar to PIP.",
      author='Ryan Bagwell',
      author_email='ryan@ryanbagwell.com',
      url='https://github.com/ryanbagwell',
      py_modules=['wordpresspm.installers', 'wordpresspm.wpm'],
      executables = [Executable("wordpresspm/wpm.py", targetDir='bin')],
      scripts=['bin/wpm'],
      classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Environment :: Web Environment',
        'Programming Language :: PHP',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: Python Software Foundation License',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows',
      ],
     )