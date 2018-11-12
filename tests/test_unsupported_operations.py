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
Unit tests for the :mod:`pennylane_pq` BasisState operation.
"""

import unittest
import logging as log
#import inspect
#from unittest_data_provider import data_provider
from pkg_resources import iter_entry_points
from defaults import pennylane as qml, BaseTest
import pennylane
from pennylane import Device
from pennylane import numpy as np
import pennylane_pq
import pennylane_pq.expval
from pennylane_pq.devices import ProjectQSimulator, ProjectQClassicalSimulator, ProjectQIBMBackend

log.getLogger('defaults')

class UnsupportedOperationTest(BaseTest):
    """test the BasisState operation.
    """

    num_subsystems = 4
    devices = None

    def setUp(self):
        super().setUp()

        self.devices = []
        if self.args.device == 'simulator' or self.args.device == 'all':
            self.devices.append(ProjectQSimulator(wires=self.num_subsystems))
        if self.args.device == 'ibm' or self.args.device == 'all':
            ibm_options = pennylane.default_config['projectq.ibm']
            if "user" in ibm_options and "password" in ibm_options:
                self.devices.append(ProjectQIBMBackend(wires=self.num_subsystems, use_hardware=False, num_runs=8*1024, user=ibm_options['user'], password=ibm_options['password']))
            else:
                log.warning("Skipping test of the ProjectQIBMBackend device because IBM login credentials could not be found in the PennyLane configuration file.")
        if self.args.device == 'classical':
            pass

    def test_unsupported_operation(self):
        if self.devices is None:
            return
        self.logTestName()

        for device in self.devices:
            @qml.qnode(device)
            def circuit():
                qml.Beamsplitter(0.2, 0.1, wires=[0,1]) #this expectation will never be supported
                return qml.expval.Homodyne(0.7, 0)

            self.assertRaises(pennylane._device.DeviceError, circuit)

    def test_unsupported_expectation(self):
        if self.devices is None:
            return
        self.logTestName()

        for device in self.devices:
            @qml.qnode(device)
            def circuit():
                return qml.expval.Homodyne(0.7, 0) #this expectation will never be supported

            self.assertRaises(pennylane._device.DeviceError, circuit)


if __name__ == '__main__':
    print('Testing PennyLane ProjectQ Plugin version ' + qml.version() + ', unsupported operations.')
    # run the tests in this file
    suite = unittest.TestSuite()
    for t in (BasisStateTest, ):
        ttt = unittest.TestLoader().loadTestsFromTestCase(t)
        suite.addTests(ttt)

    unittest.TextTestRunner().run(suite)
