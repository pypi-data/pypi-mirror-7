# -*- coding: utf-8 -*-
import codecs
import os
import re
from setuptools import setup, find_packages


def read(*parts):
    filename = os.path.join(os.path.dirname(__file__), *parts)
    with codecs.open(filename, encoding='utf-8') as fp:
        return fp.read()


def find_version(*file_paths):
    version_file = read(*file_paths)
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                              version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")


install_requires = []

setup(
    name = 'yarn-api-client',
    version = find_version('yarn_api_client', '__init__.py'),
    description='Python client for Hadoop® YARN API',
    long_description=read('README.md'),
    packages = find_packages(exclude=['tests']),

    install_requires = install_requires,
    entry_points = {
        'console_scripts': [
            'yarn_client = yarn_api_client.__main__:main',
        ],
    },

    tests_require = ['mock'],
    test_suite = 'tests',

    author = 'Iskandarov Eduard',
    author_email = 'e.iskandarov@corp.mail.ru',
    license = 'Mail.Ru Group',
    url = 'https://github.com/toidi/hadoop-yarn-api-python-client',
    classifiers = [
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.7',
        'Topic :: System :: Distributed Computing',
    ],
)
