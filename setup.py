#!/usr/bin/env python

from setuptools import setup, find_packages

for line in open('BitVector/__init__.py'):
    if line.startswith('__version__'):
        VERSION = line.split('\'')[1]
        break

setup(name='BitVector',
      version=VERSION,
      author='Avinash Kak',
      author_email='kak@purdue.edu',
      maintainer='Avinash Kak',
      maintainer_email='kak@purdue.edu',
      url='https://engineering.purdue.edu/kak/dist/BitVector-%s.html' % VERSION,
      download_url=(
          'https://engineering.purdue.edu/kak/dist/BitVector-%s.tar.gz' %
          VERSION),
      description=('Pure-Python memory-efficient packed bit arrays'),
      long_description=open('README').read(),
      license='Python Software Foundation License',
      keywords=', '.join([
          'bit array',
          'bit vector',
          'bit string',
          'logical operations on bit fields']),
      platforms='All platforms',
      classifiers=[
          'Topic :: Utilities',
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3.4'
      ],
      packages=find_packages(),
      test_suite = "test",
)
