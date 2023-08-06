# Copyright 2009-2013, Simon Kennedy, code@sffjunkie.co.uk
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from setuptools import setup, find_packages

setup(name='tks',
    version='0.1',
    description="""A collection of Tk widgets""",
    long_description="""A collection of Tk widgets for dates, times and colors.""",
    author='Simon Kennedy',
    author_email='code@sffjunkie.co.uk',
    url="http://www.sffjunkie.co.uk/python-tkstuff.html",
    license='Apache-2.0',
    packages=find_packages(),
    package_data={
      'tks': ['tks/*.txt'],
    },
    include_package_data=True,
    requires=['PIL'],
    extras_require={'idth': ['babel']},
)
