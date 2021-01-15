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
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
    ],
    description="A common bin collection for my own usage",
    entry_points={
        'console_scripts': [
            # 'py_fx_bin=py_fx_bin.cli:main',
            'fx_bin_upgrade=fx_bin.run_upgrade_program:main',
            'files=fx_bin.files:main',
            'size=fx_bin.size:main',
            'ff=fx_bin.find_files:main',
            'replace=fx_bin.replace:main',
            'grab_json_api_to_excel=fx_bin.pd:main',
            's=fx_bin.upload_server:main',
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
    version='0.3.4',
    zip_safe=False,
)
