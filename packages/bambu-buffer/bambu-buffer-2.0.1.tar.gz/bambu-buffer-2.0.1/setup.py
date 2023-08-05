#!/usr/bin/env python
from setuptools import setup
from os import path

setup(
    name = 'bambu-buffer',
    version = '2.0.1',
    description = 'Post to Buffer and manage profile settings through a Django-powered site',
    author = 'Steadman',
    author_email = 'mark@steadman.io',
    url = 'https://github.com/iamsteadman/bambu-buffer',
    long_description = open(path.join(path.dirname(__file__), 'README')).read(),
    packages = [
        'bambu_buffer',
        'bambu_buffer.migrations',
        'bambu_buffer.management',
        'bambu_buffer.management.commands'
    ],
    package_data = {
        'bambu_buffer': [
            'templates/buffer/*.html'
        ]
    },
    install_requires = [
        'Django>=1.6',
        'requests>=2.0'
    ],
    classifiers = [
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Framework :: Django'
    ]
)
