# -*- coding: utf-8 -*-
from distutils.core import setup
from setuptools import find_packages

setup(
    name='django-multilingualfield',
    packages=find_packages(),
    version='0.1',
    author=u'Jonathan Ellenberger',
    author_email='jonathan_ellenberger@wgbh.org',
    url='http://github.com/WGBH/django-multilingualfield/',
    license='MIT License, see LICENSE',
    description='A django field for storing multiple manually-written' + \
                'translations of the same piece of text.',
    long_description=open('README.md').read(),
    zip_safe=False,
)