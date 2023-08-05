#!/usr/bin/env python
# -*- coding: utf-8 -*-

# vim: tabstop=4 shiftwidth=4 softtabstop=4

#    Copyright (C) 2014 Yahoo! Inc. All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import os

from setuptools import setup


def _path(fn):
    return os.path.join(os.path.dirname(__file__), fn)


def _readme():
    with open(_path("README.rst"), "r") as handle:
        return handle.read()


setup(name='doc8',
      version='0.1.6',
      description='style checker for sphinx (or other) rst documentation.',
      url='https://github.com/harlowja/doc8',
      scripts=[
          _path(os.path.join('scripts', 'doc8')),
      ],
      license="ASL 2.0",
      install_requires=[
          'argparse',
          'six',
      ],
      classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Utilities",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python",
      ],
      keywords="rst docs style checking",
      long_description=_readme(),
     )