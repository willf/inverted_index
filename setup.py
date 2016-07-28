# -*- coding: utf-8 -*-

from setuptools import find_packages, setup

with open('README.rst') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

setup(
    name='sample',
    version='0.0.1',
    description='Simple in-memory inverted index code',
    long_description=readme,
    author='Will Fitzgerald',
    author_email='will.fitzgerald@pobox.com',
    url='https://github.com/willf/inverted_index',
    license=license,
    packages=find_packages(exclude=('tests', 'docs')))
