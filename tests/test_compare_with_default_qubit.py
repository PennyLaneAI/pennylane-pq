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
Unit tests for the :mod:`pennylane_pq` devices.
"""

import unittest
import logging as log
from defaults import pennylane as qml, BaseTest
from pennylane import numpy as np
import pennylane
from pennylane_pq.ops import SqrtSwap, SqrtX
from pennylane_pq.devices import ProjectQSimulator, ProjectQClassicalSimulator, ProjectQIBMBackend

log.getLogger('defaults')


class CompareWithDefaultQubitTest(BaseTest):
    """Compares the behavior of the ProjectQ plugin devices with the default qubit device.
    """
    num_subsystems = 4  # This should be as large as the largest gate/observable, but we cannot know that before instantiating the device. We thus check later that all gates/observables fit.

    devices = None

    def setUp(self):
        super().setUp()

        self.devices = []
        if self.args.device == 'simulator' or self.args.device == 'all':
            self.devices.append(ProjectQSimulator(wires=self.num_subsystems, verbose=True))
            self.devices.append(ProjectQSimulator(wires=self.num_subsystems, shots=20000000, verbose=True))
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

    def test_simple_circuits(self):

        default_qubit = qml.device('default.qubit', wires=4)

        for dev in self.devices:
            gates = [
                qml.PauliX(wires=0),
                qml.PauliY(wires=1),
                qml.PauliZ(wires=2),
                qml.S(wires=3),
                qml.T(wires=0),
                qml.RX(2.3, wires=1),
                qml.RY(1.3, wires=2),
                qml.RZ(3.3, wires=3),
                qml.Hadamard(wires=0),
                qml.Rot(0.1, 0.2, 0.3, wires=1),
                qml.CRot(0.1, 0.2, 0.3, wires=[2, 3]),
                qml.Toffoli(wires=[0, 1, 2]),
                qml.SWAP(wires=[1, 2]),
                qml.CSWAP(wires=[1, 2, 3]),
                qml.U1(1.0, wires=0),
                qml.U2(1.0, 2.0, wires=2),
                qml.U3(1.0, 2.0, 3.0, wires=3),
                qml.CRX(0.1, wires=[1, 2]),
                qml.CRY(0.2, wires=[2, 3]),
                qml.CRZ(0.3, wires=[3, 1]),
                qml.CZ(wires=[2, 3]),
                qml.QubitUnitary(np.array([[1, 0], [0, 1]]), wires=2),
            ]

            layers = 3
            np.random.seed(1967)
            gates_per_layers = [np.random.permutation(gates).numpy() for _ in range(layers)]

            for obs in {qml.PauliX(wires=0), qml.PauliY(wires=0), qml.PauliZ(wires=0), qml.Identity(wires=0), qml.Hadamard(wires=0)}:
                if obs.name in dev.observables:
                    def circuit():
                        """4-qubit circuit with layers of randomly selected gates and random connections for
                        multi-qubit gates."""
                        qml.BasisState(np.array([1, 0, 0, 0]), wires=[0, 1, 2, 3])
                        for gates in gates_per_layers:
                            for gate in gates:
                                if gate.name in dev.operations:
                                    qml.apply(gate)
                        return qml.expval(obs)

                    qnode_default = qml.QNode(circuit, default_qubit)
                    qnode = qml.QNode(circuit, dev)

                    assert np.allclose(qnode(), qnode_default(), atol=1e-3)

    def test_projectq_ops(self):

        results = [-1.0, -1.0]
        for i, dev in enumerate(self.devices[1:3]):

            gates = [
                qml.PauliX(wires=0),
                qml.PauliY(wires=1),
                qml.PauliZ(wires=2),
                SqrtX(wires=0),
                SqrtSwap(wires=[3, 0]),
            ]

            layers = 3
            np.random.seed(1967)
            gates_per_layers = [np.random.permutation(gates).numpy() for _ in range(layers)]

            def circuit():
                """4-qubit circuit with layers of randomly selected gates."""
                for gates in gates_per_layers:
                    for gate in gates:
                        if gate.name in dev.operations:
                            qml.apply(gate)
                return qml.expval(qml.PauliZ(0))

            qnode = qml.QNode(circuit, dev)
            assert np.allclose(qnode(), results[i], atol=1e-3)
            
