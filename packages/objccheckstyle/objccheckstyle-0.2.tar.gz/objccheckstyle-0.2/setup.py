#!/usr/bin/env python
# Copyright 2013 The ocstyle Authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Setup script for ocstyle."""

try:
  from setuptools import setup
except ImportError:
  from distutils.core import setup


setup(name='objccheckstyle',
      version='0.2',
      description='Objective-C style checker with jenkins checkstyle format support',
      author='zulkis',
      url='https://github.com/zulkis/objccheckstyle',
      package_dir={'': 'src'},
      packages=['objccheckstyle'],
      test_suite='nose.collector',
      include_package_data=True,
      install_requires=[
        'parcon==0.1.25',
        'lxml==3.3'
      ],
      entry_points={
        'console_scripts': [
          'objccheckstyle = objccheckstyle.main:main'
        ]
      },
)
