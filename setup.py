#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import kcpy

from setuptools import setup, find_packages

NAME = 'kcpy'

from pathlib import Path

README = Path('README.md')

# -*- Long Description -*-


if README.exists():
    long_description = README.read_text(encoding='utf-8')
else:
    long_description = 'See http://pypi.org/project/{}'.format(NAME)

setup(
    name='kcpy',
    version=kcpy.__version__,
    description='A kinesis consumer is purely written in python.',
    author='Hengfeng Li',
    author_email='hengf.li@gmail.com',
    license='MIT License',

    packages=find_packages(),
    package_dir={'kcpy': 'kcpy'},
    include_package_data=True,
    python_requires='>=3.5.0',
    keywords=[
        'kinesis',
        'consumer',
        'stream',
        'processing',
        'queue',
    ],
    scripts=[],
    install_requires=[
        'boto3',
    ],
    dependency_links=[],
    tests_require=[
        'pytest',
        'moto',
        'faker',
    ],
    zip_safe=False,
    long_description=long_description,
    long_description_content_type="text/markdown",
)
