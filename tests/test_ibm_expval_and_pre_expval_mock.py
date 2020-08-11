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
from defaults import pennylane as qml, BaseTest
from pennylane import DeviceError
from pennylane.wires import Wires
from pennylane_pq.devices import ProjectQIBMBackend
from unittest.mock import patch, MagicMock, PropertyMock, call
import os

token = os.getenv("IBMQX_TOKEN")
log.getLogger('defaults')


class ExpvalAndPreExpvalMock(BaseTest):
    """test pre_measure and expval of the plugin in a fake way that works without ibm credentials
    """

    def test_pre_measure(self):

        with patch('pennylane_pq.devices.ProjectQIBMBackend.obs_queue', new_callable=PropertyMock) as mock_obs_queue:
            mock_PauliX = MagicMock(wires=[0])
            mock_PauliX.name = 'PauliX'
            mock_PauliY = MagicMock(wires=[0])
            mock_PauliY.name = 'PauliY'
            mock_Hadamard = MagicMock(wires=[0])
            mock_Hadamard.name = 'Hadamard'
            mock_Hermitian = MagicMock(wires=[0])
            mock_Hermitian.name = 'Hermitian'

            mock_obs_queue.return_value = [
                mock_PauliX,
                mock_PauliY,
                mock_Hadamard,
            ]
            dev = ProjectQIBMBackend(wires=2, use_hardware=False, num_runs=8*1024, token=token, verbose=True)
            dev._eng = MagicMock()
            dev.apply = MagicMock()

            with patch('projectq.ops.All', new_callable=PropertyMock) as mock_All:
                dev.pre_measure()

            dev._eng.assert_has_calls([call.flush()])
            # The following might have to be changed in case a more elegant/efficient/different
            # implementation of the effective measurements is found
            dev.apply.assert_has_calls([call('Hadamard', [0], []),
                                        call('PauliZ', [0], []),
                                        call('S', [0], []),
                                        call('Hadamard', [0], []),
                                        call('RY', [0], [-0.7853981633974483])])


            mock_obs_queue.return_value = [
                mock_Hermitian
            ]
            with patch('projectq.ops.All', new_callable=PropertyMock) as mock_All:
                self.assertRaises(NotImplementedError, dev.pre_measure)

    def test_expval(self):

        dev = ProjectQIBMBackend(wires=2, use_hardware=False, num_runs=8*1024, token=token, verbose=True)
        dev._eng = MagicMock()
        dev._eng.backend = MagicMock()
        dev._eng.backend.get_probabilities = MagicMock()
        dev._eng.backend.get_probabilities.return_value = {'00': 0.1, '01': 0.3, '10': 0.2, '11': 0.4}

        self.assertAlmostEqual(dev.expval('PauliZ', wires=Wires([0]), par=list()), -0.2, delta=self.tol)
        self.assertAlmostEqual(dev.expval('Identity', wires=Wires([0]), par=list()), 1.0, delta=self.tol)
        self.assertRaises(NotImplementedError, dev.expval, 'Hermitian', wires=Wires([0]), par=list())


class Expval(BaseTest):
    """test expval()
    """

    def test_expval_exception_if_no_obs_queue(self):

        if self.args.device == 'ibm' or self.args.device == 'all':
            dev = ProjectQIBMBackend(wires=2, shots=1, use_hardware=False, token=token, verbose=True)
        else:
            return

        del dev.__dict__['_obs_queue']
        dev._eng = MagicMock()
        dev._eng.backend = MagicMock()
        dev._eng.backend.get_probabilities = MagicMock()
        dev._eng.backend.get_probabilities.return_value = {'00': 1.0}

        self.assertRaises(DeviceError, dev.expval, 'PauliX', wires=Wires([0]), par=list())
        self.assertRaises(DeviceError, dev.expval, 'PauliY', wires=Wires([0]), par=list())
        self.assertRaises(DeviceError, dev.expval, 'Hadamard', wires=Wires([0]), par=list())

if __name__ == '__main__':
    print('Testing PennyLane ProjectQ Plugin version ' + qml.version() + ', device expval and pre_measure.')
    # run the tests in this file
    suite = unittest.TestSuite()
    for t in (ExpvalAndPreExpvalMock, Expval):
        ttt = unittest.TestLoader().loadTestsFromTestCase(t)
        suite.addTests(ttt)

    unittest.TextTestRunner().run(suite)
