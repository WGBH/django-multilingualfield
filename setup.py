# -*- coding: utf-8 -*-
from distutils.core import setup
from setuptools import find_packages

setup(
    name='django-multilingualfield',
    packages=find_packages(),
    version='0.3',
    author=u'Jonathan Ellenberger',
    author_email='jonathan_ellenberger@wgbh.org',
    url='http://github.com/WGBH/django-multilingualfield/',
    license='MIT License, see LICENSE',
    description='A south-compatible suite of django fields that make it easy '
                'to manage multiple translations of text-based content '
                '(including files/images).',
    long_description=open('README.md').read(),
    zip_safe=False,
    install_requires=[
        'django-classy-tags>=0.3.4.1',
        'lxml>=3.1.2'
    ],
    package_data={
        'multilingualfield': [
            'static/multilingualfield/css/*.css'
        ]
    },
    classifiers=[
        'Framework :: Django',
    ]
)
