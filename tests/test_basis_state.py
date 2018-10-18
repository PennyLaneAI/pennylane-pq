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
Unit tests for the :mod:`openqml_pq` BasisState operation.
"""

import unittest
import logging as log
#import inspect
#from unittest_data_provider import data_provider
from pkg_resources import iter_entry_points
from defaults import openqml as qm, BaseTest
from openqml import Device
from openqml import numpy as np
import openqml_pq
import openqml_pq.expval
from openqml_pq.devices import ProjectQSimulator

#import traceback #todo: remove once we no longer capture the exception further down

log.getLogger('defaults')

class BasisStateTest(BaseTest):
    """test the BasisState operation.
    """
    num_subsystems = 4

    def test_basis_state(self):
        dev = ProjectQSimulator(wires=self.num_subsystems, verbose=True)

        for bits_to_flip in [np.array([0,0,0,0]), np.array([0,1,1,0]), np.array([1,1,1,0]), np.array([1,1,1,1])]:
            @qm.qnode(dev)
            def circuit():
                qm.BasisState(bits_to_flip, wires=list(range(self.num_subsystems)))
                return qm.expval.PauliZ(0), qm.expval.PauliZ(1), qm.expval.PauliZ(2), qm.expval.PauliZ(3)

            self.assertAllAlmostEqual([1]*self.num_subsystems-2*bits_to_flip, np.array(circuit()), delta=self.tol)

if __name__ == '__main__':
    print('Testing OpenQML ProjectQ Plugin version ' + qm.version() + ', BasisState operation.')
    # run the tests in this file
    suite = unittest.TestSuite()
    for t in (BasisStateTest, ):
        ttt = unittest.TestLoader().loadTestsFromTestCase(t)
        suite.addTests(ttt)

    unittest.TextTestRunner().run(suite)
