# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
from Cython.Build import cythonize

setup(
    name='python-kyototycoon-binary',
    version='0.1.5',
    description='A Python client for accessing Kyoto Tycoon via binary protocol',
    long_description=open('README.rst').read(),
    author='Studio Ousia',
    author_email='admin@ousia.jp',
    url='http://github.com/studio-ousia/python-kyototycoon-binary',
    packages=find_packages(),
    license=open('LICENSE').read(),
    ext_modules=cythonize('bkyototycoon/client.pyx'),
    include_package_data=True,
    keywords=[],
    classifiers=(
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
    ),
    install_requires=[
        'gsocketpool',
        'msgpack-python',
    ],
    tests_require=[
        'nose',
        'mock',
    ],
    test_suite = 'nose.collector'
)
