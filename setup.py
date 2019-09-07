#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = ['Click>=7.0', ]

setup_requirements = [ ]

test_requirements = [ ]

setup(
    name='fx-bin',
    author="Frank Xu",
    author_email='frank@frankxu.me',
    classifiers=[
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3.7',
    ],
    description="A common bin collection for my own usage",
    entry_points={
        'console_scripts': [
            # 'py_fx_bin=py_fx_bin.cli:main',
            'size=fx_bin.size:main',
            'ff=fx_bin.find_files:main',
        ],
    },
    install_requires=requirements,
    long_description=readme + '\n\n' + history,
    include_package_data=True,
    keywords='fx_bin',
    packages=find_packages(include=['fx_bin']),
    setup_requires=setup_requirements,
    test_suite='tests',
    tests_require=test_requirements,
    url='https://github.com/frankyxhl/py_fx_bin',
    version='0.1.13',
    zip_safe=False,
)
