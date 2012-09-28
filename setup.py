#!/usr/bin/env python
#from distutils.core import setup
from setuptools import setup, find_packages

setup(name="tumblrpy",
      version="0.1.1",
      description="Tumblr library for python",
      license="MIT",
      author="Jesse Emery",
      author_email="j@yourtrove.com",
      url="http://github.com/ejesse/tumblrpy",
      packages = find_packages(),
      keywords= "tumblr library",
      zip_safe = True)
