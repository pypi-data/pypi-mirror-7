#!/usr/bin/env python

from setuptools import setup, find_packages

setup(
    name='question-stack',
    version='0.1',
    author='Steve Yeago',
    author_email='subsume@gmail.com',
    description='Managing stackoverflow-like-situations in Django',
    url='http://github.com/subsume/question-stack',
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
