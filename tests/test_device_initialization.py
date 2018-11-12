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
#import inspect
#from unittest_data_provider import data_provider
from pkg_resources import iter_entry_points
from defaults import pennylane as qml, BaseTest
import pennylane
from pennylane import Device, DeviceError
from pennylane import numpy as np
import pennylane_pq
import pennylane_pq.expval
from pennylane_pq.devices import ProjectQSimulator, ProjectQClassicalSimulator, ProjectQIBMBackend

log.getLogger('defaults')

class DeviceInitialization(BaseTest):
    """test aspects of the device initialization.
    """

    num_subsystems = 4
    devices = None

    def test_ibm_no_user(self):
        if self.args.device == 'ibm' or self.args.device == 'all':
            self.assertRaises(ValueError, ProjectQIBMBackend, wires=self.num_subsystems, use_hardware=False, password='password')

    def test_ibm_no_password(self):
        if self.args.device == 'ibm' or self.args.device == 'all':
            self.assertRaises(ValueError, ProjectQIBMBackend, wires=self.num_subsystems, use_hardware=False, user='user')

    def test_log_verbose(self):
        dev = ProjectQIBMBackend(wires=self.num_subsystems, log=True, use_hardware=False, user="user", password='password')
        self.assertEqual(dev.kwargs['log'],True)
        self.assertEqual(dev.kwargs['log'],dev.kwargs['verbose'])

    def test_shots(self):
        if self.args.device == 'ibm' or self.args.device == 'all':
            shots = 5
            dev1 = ProjectQIBMBackend(wires=self.num_subsystems, shots=shots, use_hardware=False, user="user", password='password')
            self.assertEqual(shots, dev1.shots)
            self.assertEqual(shots, dev1.kwargs['num_runs'])

            dev2 = ProjectQIBMBackend(wires=self.num_subsystems, num_runs=shots, use_hardware=False, user="user", password='password')
            self.assertEqual(shots, dev2.shots)
            self.assertEqual(shots, dev2.kwargs['num_runs'])

            dev2 = ProjectQIBMBackend(wires=self.num_subsystems, shots=shots+2, num_runs=shots, use_hardware=False, user="user", password='password')
            self.assertEqual(shots, dev2.shots)
            self.assertEqual(shots, dev2.kwargs['num_runs'])

    def test_initiatlization_via_pennylane(self):
        for short_name in [
                'projectq.simulator',
                'projectq.classical',
                'projectq.ibm'
        ]:
            try:
                dev = dev = qml.device(short_name, wires=2)
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
