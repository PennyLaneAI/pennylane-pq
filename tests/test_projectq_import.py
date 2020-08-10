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
"""
Unit tests for the :mod:`pennylane_pq` devices' behavior when applying unsupported operations.
"""

import unittest
import logging as log
import sys
from unittest import mock
from pkg_resources import iter_entry_points
from defaults import pennylane as qml, BaseTest

log.getLogger('defaults')


class ProjectQImportTest(BaseTest):
    """test of projectq import.
    """

    def test_projectq_import(self):
        """Check that from projectq.ops import MatrixGate can raise an exception without problems, this ensures backward compatibility with older versions of ProjectQ
        """
        del sys.modules["pennylane_pq.pqops"]
        import projectq.ops
        if 'MatrixGate' in projectq.ops.__dict__:
            del projectq.ops.__dict__['MatrixGate']
        import pennylane_pq.pqops

        del sys.modules["pennylane_pq.pqops"]
        import projectq.ops
        if 'MatrixGate' not in projectq.ops.__dict__:
            projectq.ops.__dict__['MatrixGate'] = projectq.ops.__dict__['BasicGate']
        import pennylane_pq.pqops

        # restore
        del sys.modules["projectq.ops"]
        import pennylane_pq.pqops

if __name__ == '__main__':
    print('Testing PennyLane ProjectQ Plugin version ' + qml.version() + ', import test.')
    # run the tests in this file
    suite = unittest.TestSuite()
    for t in (ProjectQImportTest, ):
        ttt = unittest.TestLoader().loadTestsFromTestCase(t)
        suite.addTests(ttt)

    unittest.TextTestRunner().run(suite)
