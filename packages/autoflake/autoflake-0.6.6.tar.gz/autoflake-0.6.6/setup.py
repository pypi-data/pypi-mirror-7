#!/usr/bin/env python
"""Setup for autoflake."""

import ast

import setuptools


def version():
    """Return version string."""
    with open('autoflake.py') as input_file:
        for line in input_file:
            if line.startswith('__version__'):
                return ast.parse(line).body[0].value.s


with open('README.rst') as readme:
    setuptools.setup(
        name='autoflake',
        version=version(),
        description='Removes unused imports and unused variables.',
        long_description=readme.read(),
        license='Expat License',
        author='Steven Myint',
        url='https://github.com/myint/autoflake',
        classifiers=['Environment :: Console',
                     'Intended Audience :: Developers',
                     'License :: OSI Approved :: MIT License',
                     'Programming Language :: Python :: 2.7',
                     'Programming Language :: Python :: 3',
                     'Programming Language :: Python :: 3.2',
                     'Programming Language :: Python :: 3.3',
                     'Programming Language :: Python :: 3.4',
                     'Topic :: Software Development :: Quality Assurance'],
        keywords='clean,fix,automatic,unused,import',
        py_modules=['autoflake'],
        entry_points={
            'console_scripts': ['autoflake = autoflake:main']},
        install_requires=['pyflakes>=0.8.1'],
        test_suite='test_autoflake')
