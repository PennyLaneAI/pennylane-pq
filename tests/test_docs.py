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
Unit tests for the :mod:`pennylane_pq` device documentation
"""

import unittest
import logging as log
import re
from pkg_resources import iter_entry_points
from defaults import pennylane as qml, BaseTest
import pennylane
from pennylane import Device, DeviceError
from pennylane import numpy as np
import pennylane_pq
import pennylane_pq.expval
from pennylane_pq.devices import ProjectQSimulator, ProjectQClassicalSimulator, ProjectQIBMBackend

log.getLogger('defaults')

class DocumentationTest(BaseTest):
    """test documentation of the plugin.
    """

    num_subsystems = 4
    devices = None

    devices = None
    def setUp(self):
        super().setUp()

        self.devices = []
        if self.args.device == 'simulator' or self.args.device == 'all':
            self.devices.append(ProjectQSimulator(wires=self.num_subsystems))
            self.devices.append(ProjectQSimulator(wires=self.num_subsystems, shots=20000000))
        if self.args.device == 'ibm' or self.args.device == 'all':
            ibm_options = pennylane.default_config['projectq.ibm']
            if "user" in ibm_options and "password" in ibm_options:
                self.devices.append(ProjectQIBMBackend(wires=self.num_subsystems, use_hardware=False, num_runs=8*1024, user=ibm_options['user'], password=ibm_options['password']))
            else:
                log.warning("Skipping test of the ProjectQIBMBackend device because IBM login credentials could not be found in the PennyLane configuration file.")
        if self.args.device == 'classical' or self.args.device == 'all':
            self.devices.append(ProjectQClassicalSimulator(wires=self.num_subsystems))

    def test_device_docstrings(self):
        for dev in self.devices:
            docstring = dev.__doc__
            supp_operations = dev.operations
            supp_expectations = dev.expectations
            #print(docstring)
            documented_operations = ([ re.findall(r"(?:pennylane\.|pennylane_pq.ops\.)([^`> ]*)", string) for string in re.findall(r"(?:(?:Extra|Supported PennyLane) Operations:\n((?:\s*:class:`[^`]+`,?\n)*))", docstring, re.MULTILINE)])
            documented_operations = set([item for sublist in documented_operations for item in sublist])

            documented_expectations = ([ re.findall(r"(?:pennylane\.expval\.|pennylane_pq\.expval\.)([^`> ]*)", string) for string in re.findall(r"(?:(?:Extra|Supported PennyLane) Expectations:\n((?:\s*:class:`[^`]+`,?\n)*))", docstring, re.MULTILINE)])
            documented_expectations = set([item for sublist in documented_expectations for item in sublist])

            supported_but_not_documented_operations = supp_operations.difference(documented_operations)
            self.assertFalse(supported_but_not_documented_operations, msg="For device "+dev.short_name+" the Operations "+str(supported_but_not_documented_operations)+" are supported but not documented.")
            documented_but_not_supported_operations = documented_operations.difference(supp_operations)
            self.assertFalse(documented_but_not_supported_operations, msg="For device "+dev.short_name+" the Operations "+str(documented_but_not_supported_operations)+" are documented but not actually supported.")

            supported_but_not_documented_expectations = supp_expectations.difference(documented_expectations)
            self.assertFalse(supported_but_not_documented_expectations, msg="For device "+dev.short_name+" the Expectations "+str(supported_but_not_documented_expectations)+" are supported but not documented.")
            documented_but_not_supported_expectations = documented_expectations.difference(supp_expectations)
            self.assertFalse(documented_but_not_supported_expectations, msg="For device "+dev.short_name+" the Expectations "+str(documented_but_not_supported_expectations)+" are documented but not actually supported.")





    # def test_ibm_no_user(self):
    #     if self.args.device == 'ibm' or self.args.device == 'all':
    #         self.assertRaises(ValueError, ProjectQIBMBackend, wires=self.num_subsystems, use_hardware=False, password='password')

    # def test_ibm_no_password(self):
    #     if self.args.device == 'ibm' or self.args.device == 'all':
    #         self.assertRaises(ValueError, ProjectQIBMBackend, wires=self.num_subsystems, use_hardware=False, user='user')

    # def test_log_verbose(self):
    #     dev = ProjectQIBMBackend(wires=self.num_subsystems, log=True, use_hardware=False, user="user", password='password')
    #     self.assertEqual(dev.kwargs['log'],True)
    #     self.assertEqual(dev.kwargs['log'],dev.kwargs['verbose'])

    # def test_shots(self):
    #     if self.args.device == 'ibm' or self.args.device == 'all':
    #         shots = 5
    #         dev1 = ProjectQIBMBackend(wires=self.num_subsystems, shots=shots, use_hardware=False, user="user", password='password')
    #         self.assertEqual(shots, dev1.shots)
    #         self.assertEqual(shots, dev1.kwargs['num_runs'])

    #         dev2 = ProjectQIBMBackend(wires=self.num_subsystems, num_runs=shots, use_hardware=False, user="user", password='password')
    #         self.assertEqual(shots, dev2.shots)
    #         self.assertEqual(shots, dev2.kwargs['num_runs'])

    #         dev2 = ProjectQIBMBackend(wires=self.num_subsystems, shots=shots+2, num_runs=shots, use_hardware=False, user="user", password='password')
    #         self.assertEqual(shots, dev2.shots)
    #         self.assertEqual(shots, dev2.kwargs['num_runs'])

    # def test_initiatlization_via_pennylane(self):
    #     for short_name in [
    #             'projectq.simulator',
    #             'projectq.classical',
    #             'projectq.ibm'
    #     ]:
    #         try:
    #             dev = dev = qml.device(short_name, wires=2, user='user', password='password')
    #         except DeviceError:
    #             raise Exception("This test is expected to fail until pennylane-pq is installed.")

if __name__ == '__main__':
    print('Testing PennyLane ProjectQ Plugin version ' + qml.version() + ', device initialization.')
    # run the tests in this file
    suite = unittest.TestSuite()
    for t in (DocumentationTest, ):
        ttt = unittest.TestLoader().loadTestsFromTestCase(t)
        suite.addTests(ttt)

    unittest.TextTestRunner().run(suite)
