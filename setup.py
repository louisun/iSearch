#!/usr/bin/env python
# coding=utf-8

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

import iSearch

setup(
    name='iSearch',
    keywords=['dictionary', 'youdao', 'word'],
    version=iSearch.__version__,
    packages=['iSearch'],
    url='https://github.com/louisun/iSearch',
    license='MIT',
    author='louisun',
    author_email='luyang.sun@outlook.com',
    description='有道词典单词查询、存储和管理的命令行工具',
    install_requires=[
        'requests','termcolor','bs4'
    ],
    entry_points = {
        'console_scripts': [
            's = iSearch.isearch:main'
        ]
    },
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)