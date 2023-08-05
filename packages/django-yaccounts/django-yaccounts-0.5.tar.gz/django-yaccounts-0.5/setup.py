#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
from setuptools import setup

README = open(os.path.join(os.path.dirname(__file__), 'README.rst')).read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='django-yaccounts',
    version='0.5',
    packages=['yaccounts'],
    include_package_data=True,
    license='BSD License',  # example license
    description='Accounts app.',
    #long_description=README,
    #url='http://www.example.com/',
    author='André Tavares',
    author_email='github@andretavares.com',
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License', # example license
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
    install_requires=[
        'PIL==1.1.7',
        'python-twitter==1.1',
        'facebook-sdk==0.4.0',
        'django-yapi',
        'django-yutils'
    ]
)