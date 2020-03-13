#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

with open('README.md') as readme:
    long_description = readme.read()

setup(
    name='talentlms',
    version='1.0.1',
    description='TalentLMS API Python library',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/ib1984/py-talentlms',
    author='Ivan Butorin',
    author_email='ibutorin@plesk.com',
    license='MIT',
    packages=[
        'talentlms'
    ],
    python_requires='>=2.7',
    install_requires=[
        'requests'
    ],
    classifiers=[
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
        'License :: OSI Approved :: MIT License',
        'Topic :: Software Development :: Libraries',
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology'
    ]
)
