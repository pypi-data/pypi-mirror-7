#!/usr/bin/env python

"""AzkabanCLI: a lightweight command line interface for Azkaban."""

from azkaban import __version__
from setuptools import find_packages, setup

setup(
    name='azkaban',
    version=__version__,
    description='AzkabanCLI',
    long_description=open('README.rst').read(),
    author='Matthieu Monsch',
    author_email='monsch@alum.mit.edu',
    url='http://azkabancli.readthedocs.org/',
    license='MIT',
    # py_modules=['azkaban'],
    packages=find_packages(),
    classifiers=[
      'Development Status :: 4 - Beta',
      'Intended Audience :: Developers',
      'License :: OSI Approved :: MIT License',
      'Programming Language :: Python',
    ],
    install_requires=[
      'docopt',
      'requests>=2.0.1',
    ],
    entry_points={'console_scripts': [
      'azkaban = azkaban.__main__:main',
      'azkabanpig = azkaban.ext.pig:main',
    ]},
)
