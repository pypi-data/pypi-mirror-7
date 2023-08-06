#!/usr/bin/env python

from io import open
import os
import sys

from setuptools import setup, find_packages

readme = open('README.rst', encoding='utf-8').read()

setup(name='geoffrey-todo',
      version='0.0.1',
      description='Collects all TODO notes in source files.',
      long_description=readme,
      author='Roberto Abdelkader Martínez Pérez',
      author_email='robertomartinezp@gmail.com',
      url='https://github.com/nilp0inter/geoffrey-todo',
      include_package_data=True,
      packages=find_packages(),
      namespace_package=['geoffrey.plugins'],
)