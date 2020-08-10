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
from defaults import pennylane as qml, BaseTest
import pennylane
from pennylane_pq.devices import ProjectQSimulator, ProjectQClassicalSimulator, ProjectQIBMBackend

log.getLogger('defaults')


class UnsupportedOperationTest(BaseTest):
    """test that unsupported operations/expectations raise DeviceErrors.
    """

    num_subsystems = 4
    devices = None

    def setUp(self):
        super().setUp()

        self.devices = []
        if self.args.device == 'simulator' or self.args.device == 'all':
            self.devices.append(ProjectQSimulator(wires=self.num_subsystems, verbose=True))
        if self.args.device == 'ibm' or self.args.device == 'all':
            ibm_options = pennylane.default_config['projectq.ibm']
            if "token" in ibm_options:
                self.devices.append(ProjectQIBMBackend(wires=self.num_subsystems, use_hardware=False, num_runs=8 * 1024,
                                                       token=ibm_options['token'], verbose=True))
            else:
                log.warning("Skipping test of the ProjectQIBMBackend device because IBM login credentials "
                            "could not be found in the PennyLane configuration file.")
        if self.args.device == 'classical' or self.args.device == 'all':
            self.devices.append(ProjectQClassicalSimulator(wires=self.num_subsystems, verbose=True))

    def test_unsupported_operation(self):
        if self.devices is None:
            return
        self.logTestName()

        class SomeOperation(qml.operation.Operation):
            num_params = 0
            num_wires = 1
            par_domain = 'A'

        for device in self.devices:
            @qml.qnode(device)
            def circuit():
                SomeOperation(wires=0)
                return qml.expval(qml.PauliZ(0))

            self.assertRaises(pennylane._device.DeviceError, circuit)

    def test_unsupported_expectation(self):
        if self.devices is None:
            return
        self.logTestName()

        class SomeObservable(qml.operation.Observable):
            num_params = 0
            num_wires = 1
            par_domain = 'A'

        for device in self.devices:
            @qml.qnode(device)
            def circuit():
                return qml.expval(SomeObservable(wires=0)) #this expectation will never be supported

            self.assertRaises(pennylane._device.DeviceError, circuit)


if __name__ == '__main__':
    print('Testing PennyLane ProjectQ Plugin version ' + qml.version() + ', unsupported operations.')
    # run the tests in this file
    suite = unittest.TestSuite()
    for t in (UnsupportedOperationTest, ):
        ttt = unittest.TestLoader().loadTestsFromTestCase(t)
        suite.addTests(ttt)

    unittest.TextTestRunner().run(suite)
