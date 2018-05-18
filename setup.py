# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

from setuptools import find_packages, setup

setup(
    name='wwe',
    version='0.0.1',
    description='',  # TODO
    long_description=open('README.rst').read(),  # TODO: Remember to change the README to rst markup
    url='https://github.com/dtgoitia/py-wwe',
    author='David Torralba Goitia',
    author_email='dtgoitia@gmail.com',
    classifiers=[
        'Development Status :: 1 - Planning',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.6',
        # TODO: Look in pypi.org for other classifiers
    ],
    packages=find_packages(exclude=['tests']),
    license='MIT',
    python_requires='>=3.6',
    include_package_data=True,
    zip_safe=False,
    keywords=['toggl'],  # TODO: Add relevant tags
    install_requires=[
        'tapioca-toggl',  # TODO: Automate extraction from Pipfile?
    ],
)
