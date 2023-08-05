#!/usr/bin/env python
from distutils.core import setup
from distutils.command.install_data import install_data

setup(name='Wordpress-Package-Manager',
      version='0.8.3',
      description='A command-line tool for installing WordPress plugins',
      long_description="A command-line tool for installing WordPress plugins in a manner similar to PIP.",
      author='Ryan Bagwell',
      author_email='ryan@ryanbagwell.com',
      url='https://github.com/ryanbagwell',
      py_modules=['wordpresspm.installers', 'wordpresspm.wpm'],
      scripts=['wordpresspm/wpm'],
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
      ]
    )
