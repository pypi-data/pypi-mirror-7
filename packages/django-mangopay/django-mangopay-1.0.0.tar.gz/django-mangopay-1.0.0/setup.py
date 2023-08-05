#!/usr/bin/env python

from setuptools import setup, find_packages
import mangopay

setup(
    name='django-mangopay',
    version=".".join(map(str, mangopay.__version__)),
    author='Rebecca Meritz',
    author_email='rebecca@fundedbyme.com',
    url='http://github.com/FundedByMe/django-mangopay',
    install_requires=[
        'Django>=1.4.3',
        'mangopaysdk==0.311',
    ],
    description='Django package that helps in your Mangopay integration',
    packages=find_packages(),
    include_package_data=True,
    classifiers=[
        "Framework :: Django",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "Operating System :: OS Independent",
        "Topic :: Software Development"
    ],
)
