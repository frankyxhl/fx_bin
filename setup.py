#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = ['Click>=8.1.3', 'loguru>=0.7.0' ]

setup_requirements = []

test_requirements = []

setup(
    name='fx-bin',
    author="Frank Xu",
    author_email='frank@frankxu.me',
    classifiers=[
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
    ],
    description="A common bin collection for my own usage",
    entry_points={
        'console_scripts': [
            'fx_upgrade=fx_bin.run_upgrade_program:main',
            'fx_files=fx_bin.files:main',
            'fx_size=fx_bin.size:main',
            'fx_ff=fx_bin.find_files:main',
            'fx_replace=fx_bin.replace:main',
            'fx_grab_json_api_to_excel=fx_bin.pd:main',
            'fx_server=fx_bin.upload_server:main',
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
    url='https://github.com/frankyxhl/fx_bin',
    version='0.6.2',
    zip_safe=False,
)
