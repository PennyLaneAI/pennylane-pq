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
Unit tests for the :mod:`pennylane_pq` device initialization
"""

import unittest
import logging as log
from defaults import pennylane as qml, BaseTest
from pennylane import DeviceError
from pennylane_pq.devices import ProjectQIBMBackend
import os

token = os.getenv("IBMQX_TOKEN")
log.getLogger('defaults')


class DeviceInitialization(BaseTest):
    """test aspects of the device initialization.
    """

    num_subsystems = 4
    devices = None

    def test_ibm_no_token(self):
        if self.args.device == 'ibm' or self.args.device == 'all':
            self.assertRaises(ValueError, ProjectQIBMBackend, wires=self.num_subsystems, use_hardware=False)

    def test_shots(self):
        if self.args.device == 'ibm' or self.args.device == 'all':
            shots = 5
            dev1 = ProjectQIBMBackend(wires=self.num_subsystems, shots=shots, use_hardware=False, token=token, verbose=True)
            self.assertEqual(shots, dev1.shots)

            dev2 = ProjectQIBMBackend(wires=self.num_subsystems, num_runs=shots, use_hardware=False, token=token)
            self.assertEqual(shots, dev2.shots)

            dev2 = ProjectQIBMBackend(wires=self.num_subsystems, shots=shots+2, num_runs=shots, use_hardware=False,
                                      token=token)
            self.assertEqual(shots, dev2.shots)

    def test_initiatlization_via_pennylane(self):
        for short_name in [
                'projectq.simulator',
                'projectq.classical',
                'projectq.ibm'
        ]:
            try:
                dev = qml.device(short_name, wires=2, token=token, verbose=True)
            except DeviceError:
                raise Exception("This test is expected to fail until pennylane-pq is installed.")


if __name__ == '__main__':
    print('Testing PennyLane ProjectQ Plugin version ' + qml.version() + ', device initialization.')
    # run the tests in this file
    suite = unittest.TestSuite()
    for t in (DeviceInitialization, ):
        ttt = unittest.TestLoader().loadTestsFromTestCase(t)
        suite.addTests(ttt)

    unittest.TextTestRunner().run(suite)
