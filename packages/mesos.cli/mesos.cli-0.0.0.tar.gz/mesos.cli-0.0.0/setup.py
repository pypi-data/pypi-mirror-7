# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import imp
import os

mod = imp.load_source('mesos.cli', os.path.join(os.path.dirname(__file__),
    "mesos", "cli", "__init__.py"))

with open(os.path.join(os.path.dirname(__file__), "README.rst")) as f:
  readme = f.read()

requires = [
    "argcomplete>=0.8.0",
    "blessings>=1.5.1",
    "gevent>=1.0.1",
    "importlib>=1.0.3", # py26
    "kazoo>=2.0",
    "mesos.interface>=0.20.0",
    "ordereddict>=1.1", # py26
    "prettytable>=0.7.2",
    "protobuf>=2.5.0,<3",
    "requests>=2.2.1"
]

config = {
    'name': 'mesos.cli',
    'version': mod.__version__,
    'description': 'Mesos CLI Tools',
    'long_description': readme,
    'author': 'Thomas Rampelberg',
    'author_email': 'thomas@mesosphere.io',
    'url': 'http://pypi.python.org/pypi/mesos.cli',
    'license': 'Apache 2.0',
    'keywords': 'mesos',
    'classifiers': [ ],

    'namespace_packages': [ 'mesos' ],
    'packages': [ 'mesos', 'mesos.cli' ],
    'entry_points': {
        'console_scripts': [
            'mesos = mesos.cli.main:main',

            # helpers
            'mesos-completion = mesos.cli.completion:main',
            'mesos-config = mesos.cli.config:main',
            'mesos-resolve = mesos.cli.resolve:main',
            'mesos-state = mesos.cli.state:main',

            # coreutils
            'mesos-cat = mesos.cli.cat:main',
            'mesos-find = mesos.cli.find:main',
            'mesos-head = mesos.cli.head:main',
            'mesos-help = mesos.cli.help:main',
            'mesos-ls = mesos.cli.ls:main',
            'mesos-ps = mesos.cli.ps:main',
            'mesos-scp = mesos.cli.scp:main',
            'mesos-ssh = mesos.cli.ssh:main',
            'mesos-tail = mesos.cli.tail:main'
        ]
    },
    'setup_requires': [
        "nose>=1.3.3",
        "tox>=1.7.1"
    ],
    'install_requires': requires,
    'tests_require': [
        'coverage>=3.7.1',
        'mock>=1.0.1',
        'testtools>=0.9.35', # py26
        'zake>=0.0.20'
    ],
    'test_suite': 'nose.collector',
    'scripts': [
        'bin/mesos-zsh-completion.sh'
    ]
}

if __name__ == "__main__":
    from setuptools import setup

    setup(**config)
