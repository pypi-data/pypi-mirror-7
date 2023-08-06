#!/usr/bin/env python

from setuptools import setup, find_packages

setup(
    name='flowy',
    version='0.2.1',
    description="Python library for Amazon Simple Workflow Service",
    long_description=open('README.rst').read(),
    keywords='amazon swf simple workflow',
    author='Sever Banesiu',
    author_email='banesiu.sever@gmail.com',
    url='https://github.com/pbs/flowy',
    license='MIT License',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=['boto==2.19.0', 'venusian>=1.0a8', 'nose>=1.0'],
    tests_require=['mock', 'coverage'],
    test_suite="nose.collector",
)
