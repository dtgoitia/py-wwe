# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

from setuptools import find_packages, setup
import json

with open('Pipfile.lock') as fd:
    lock_data = json.load(fd)

    install_requires = []
    for package_name, package_data in lock_data['default'].items():
        if 'version' not in package_data:
            raise ValueError(f'Package {package_name} does '
                             f'not have version key: {package_data}')
        install_requires.append(package_name + package_data['version'])

setup(
    name='wwe',
    version='0.0.1',
    description='',  # TODO
    # TODO: Remember to change the README to rst markup
    long_description=open('README.rst').read(),
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
    keywords=['toggl'],     # TODO: Add relevant tags
    install_requires=install_requires,
    entry_points={
        "console_scripts": [
            'wwe=wwe.cli:main',
        ],
    }
)
