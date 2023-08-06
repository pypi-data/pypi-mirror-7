#!/usr/bin/env python

from distutils.core import setup

setup(name='LinkHeader',
      version='0.4.2',
      description='Parse and format link headers according to RFC 5988 "Web Linking"',
      author='Michael Burrows',
      author_email='mjb@asplake.co.uk',
      url='http://bitbucket.org/asplake/link_header',
      py_modules=['link_header'],
      classifiers=["Development Status :: 3 - Alpha",
                   "Intended Audience :: Developers",
                   "License :: OSI Approved :: BSD License",
                   "Programming Language :: Python :: 2",
                   "Programming Language :: Python :: 3",
                   "Topic :: Internet :: WWW/HTTP",
                   "Topic :: Software Development :: Libraries :: Python Modules"])
