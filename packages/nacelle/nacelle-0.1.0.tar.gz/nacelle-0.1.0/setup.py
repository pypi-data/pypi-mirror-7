#!/usr/bin/env python
# -*- coding: utf-8 -*-

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


setup(
    name='nacelle',
    version='0.1.0',
    description='A lightweight Python framework (built on top of webapp2) for use on Google Appengine',
    long_description=open('README.rst').read(),
    author='Patrick Carey',
    author_email='patrick@rehabstudio.com',
    url='https://github.com/nacelle/nacelle',
    packages=[
        'nacelle',
    ],
    package_dir={'nacelle':
                 'nacelle'},
    include_package_data=True,
    license="MIT",
    zip_safe=False,
    keywords='nacelle',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.7',
    ],
)
