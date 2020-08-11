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
from defaults import pennylane as qml, BaseTest
from pennylane_pq.devices import ProjectQSimulator, ProjectQClassicalSimulator, ProjectQIBMBackend
import os

token = os.getenv("IBMQX_TOKEN")
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
            self.devices.append(ProjectQIBMBackend(wires=self.num_subsystems, use_hardware=False, num_runs=8 * 1024,
                                                   token=token, verbose=True))
        if self.args.device == 'classical' or self.args.device == 'all':
            self.devices.append(ProjectQClassicalSimulator(wires=self.num_subsystems))

    def test_device_docstrings(self):
        for dev in self.devices:
            docstring = dev.__doc__
            supp_operations = dev.operations
            supp_observables = dev.observables
            #print(docstring)
            documented_operations = ([ re.findall(r"(?:pennylane\.|pennylane_pq.ops\.)([^`> ]*)", string) for string in re.findall(r"(?:(?:Extra|Supported PennyLane) Operations:\n((?:\s*:class:`[^`]+`,?\n)*))", docstring, re.MULTILINE)])
            documented_operations = set([item for sublist in documented_operations for item in sublist])

            documented_observables = ([ re.findall(r"(?:pennylane\.|pennylane_pq\.)([^`> ]*)", string) for string in re.findall(r"(?:(?:Extra|Supported PennyLane) observables:\n((?:\s*:class:`[^`]+`,?\n)*))", docstring, re.MULTILINE)])
            documented_observables = set([item for sublist in documented_observables for item in sublist])

            supported_but_not_documented_operations = supp_operations.difference(documented_operations)
            self.assertFalse(supported_but_not_documented_operations, msg="For device "+dev.short_name+" the Operations "+str(supported_but_not_documented_operations)+" are supported but not documented.")
            documented_but_not_supported_operations = documented_operations.difference(supp_operations)
            self.assertFalse(documented_but_not_supported_operations, msg="For device "+dev.short_name+" the Operations "+str(documented_but_not_supported_operations)+" are documented but not actually supported.")

            supported_but_not_documented_observables = supp_observables.difference(documented_observables)
            self.assertFalse(supported_but_not_documented_observables, msg="For device "+dev.short_name+" the Observables "+str(supported_but_not_documented_observables)+" are supported but not documented.")
            documented_but_not_supported_observables = documented_observables.difference(supp_observables)
            self.assertFalse(documented_but_not_supported_observables, msg="For device "+dev.short_name+" the Observables "+str(documented_but_not_supported_observables)+" are documented but not actually supported.")


if __name__ == '__main__':
    print('Testing PennyLane ProjectQ Plugin version ' + qml.version() + ', device documentation.')
    # run the tests in this file
    suite = unittest.TestSuite()
    for t in (DocumentationTest, ):
        ttt = unittest.TestLoader().loadTestsFromTestCase(t)
        suite.addTests(ttt)

    unittest.TextTestRunner().run(suite)
