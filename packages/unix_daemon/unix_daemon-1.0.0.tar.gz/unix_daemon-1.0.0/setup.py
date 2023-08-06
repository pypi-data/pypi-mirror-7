# -*- coding: utf-8 -*-

'''
Copyright 2014 Yoshida Shin

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
'''

from setuptools import setup

long_description = open('docs/README.rst').read()

classifiers = [
    "Development Status :: 5 - Production/Stable",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: Apache Software License",
    "Programming Language :: Python",
    "Programming Language :: Python :: 2",
    "Programming Language :: Python :: 2.6",
    "Programming Language :: Python :: 2.7",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.1",
    "Programming Language :: Python :: 3.2",
    "Programming Language :: Python :: 3.3",
    "Programming Language :: Python :: 3.4",
    "Topic :: Software Development",
    "Topic :: Software Development :: Libraries",
    "Topic :: Software Development :: Libraries :: Python Modules",
]

setup(
    name='unix_daemon',
    version='1.0.0',
    description='Function emulating Daemon(3) on Linux and Unix OS.',
    long_description=long_description,
    author='Yoshida Shin',
    author_email='wbcchsyn@gmail.com',
    url='https://github.com/wbcchsyn/unix_daemon',
    platforms=['linux', 'unix'],
    py_modules=['unix_daemon'],
    package_dir={"": "src"},
    license=['Apache License 2.0'],
    classifiers=classifiers,
)
