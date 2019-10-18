# Copyright 2018 Xanadu Quantum Technologies Inc.

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

#!/usr/bin/env python3
from setuptools import setup

with open("pennylane_pq/_version.py") as f:
    version = f.readlines()[-1].split()[-1].strip("\"'")  # pylint: disable=invalid-name


requirements = ["projectq>=0.4.1", "pennylane>=0.6"]  # pylint: disable=invalid-name


info = {  # pylint: disable=invalid-name
    "name": "PennyLane-PQ",
    "version": version,
    "maintainer": "Xanadu Inc.",
    "maintainer_email": "software@xanadu.ai",
    "url": "https://github.com/XanaduAI/PennyLane-PQ",
    "license": "Apache License 2.0",
    "packages": ["pennylane_pq"],
    "entry_points": {
        "pennylane.plugins": [
            "projectq.simulator = pennylane_pq:ProjectQSimulator",
            "projectq.classical = pennylane_pq:ProjectQClassicalSimulator",
            "projectq.ibm = pennylane_pq:ProjectQIBMBackend",
        ]
    },
    "description": "PennyLane plugin for ProjectQ",
    "long_description": open("README.rst").read(),
    "provides": ["pennylane_pq"],
    "install_requires": requirements,
}

classifiers = [  # pylint: disable=invalid-name
    "Development Status :: 4 - Beta",
    "Environment :: Console",
    "Intended Audience :: Science/Research",
    "License :: OSI Approved :: Apache Software License",
    "Natural Language :: English",
    "Operating System :: POSIX",
    "Operating System :: MacOS :: MacOS X",
    "Operating System :: POSIX :: Linux",
    "Operating System :: Microsoft :: Windows",
    "Programming Language :: Python",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.5",
    "Programming Language :: Python :: 3.6",
    "Programming Language :: Python :: 3.7",
    "Programming Language :: Python :: 3 :: Only",
    "Topic :: Scientific/Engineering :: Physics",
]

setup(classifiers=classifiers, **(info))
