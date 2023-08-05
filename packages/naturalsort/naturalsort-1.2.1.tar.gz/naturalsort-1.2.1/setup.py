#!/usr/bin/env python

from os.path import abspath, dirname, join
from setuptools import setup, find_packages

# Fill in the long description (for the benefit of PyPi)
# with the contents of README.rst (rendered by GitHub).
readme_file = join(dirname(abspath(__file__)), 'README.rst')
readme_text = open(readme_file, 'r').read()

setup(name='naturalsort',
      version='1.2.1',
      description="Simple natural order sorting API for Python",
      long_description=readme_text,
      url='https://github.com/xolox/python-naturalsort',
      author='Peter Odding',
      author_email='peter@peterodding.com',
      packages=find_packages(),
      test_suite='natsort.tests')
