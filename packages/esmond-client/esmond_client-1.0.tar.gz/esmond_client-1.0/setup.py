#!/usr/bin/env python

from setuptools import setup

setup(
    name='esmond_client',
    version='1.0',
    description='esmond API client libraries',
    long_description='esmond API client libraries.',
    author='Monte M. Goode',
    author_email='MMGoode@lbl.gov',
    url='https://github.com/esnet/esmond',
    packages=['esmond_client'],
    install_requires=['requests'],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Intended Audience :: Telecommunications Industry',
        'Environment :: Console',
        'License :: OSI Approved :: BSD License',
        'Operating System :: POSIX',
        'Programming Language :: Python :: 2',
        'Topic :: Internet',
        'Topic :: System :: Networking',
        'Topic :: Software Development :: Libraries',
    ],
)
