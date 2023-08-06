#!/usr/bin/env python

from setuptools import setup

setup(
    name='namedentities',
    version='1.6.3',
    author='Jonathan Eunice',
    author_email='jonathan.eunice@gmail.com',
    description='Easy conversion between Unicode characters and HTML entities (whether named, decimal numeric, or hex numeric)',
    long_description=open('README.rst').read(),
    url='http://bitbucket.org/jeunice/namedentities',
    packages=['namedentities'],
    install_requires=[],
    tests_require = ['tox', 'pytest','six'],
    zip_safe = True,
    keywords='HTML named numeric entities Unicode glyph character set charset',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Operating System :: OS Independent',
        'License :: OSI Approved :: BSD License',
        'Intended Audience :: Developers',
        'Environment :: Web Environment',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Topic :: Text Processing :: Filters',
        'Topic :: Text Processing :: Markup :: HTML'
    ]
)
