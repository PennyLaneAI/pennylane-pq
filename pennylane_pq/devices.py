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
# pylint: disable=expression-not-assigned
r"""
Devices
=======

.. currentmodule:: pennylane_pq.devices

This plugin offers access to the following ProjectQ backends by providing corresponding PennyLane devices:

.. autosummary::
   :nosignatures:

   ProjectQSimulator
   ProjectQIBMBackend
   ProjectQClassicalSimulator

See below for a description of the devices and the supported Operations and Expectations.

ProjectQSimulator
#################

.. autoclass:: ProjectQSimulator

ProjectQIBMBackend
##################

.. autoclass:: ProjectQIBMBackend

ProjectQClassicalSimulator
##########################

.. autoclass:: ProjectQClassicalSimulator


"""
import logging as log

import projectq as pq
from projectq.ops import (HGate, XGate, YGate, ZGate, SGate, TGate, SqrtXGate, SwapGate, SqrtSwapGate, Rx, Ry, Rz, R, StatePreparation)

from pennylane import Device, DeviceError

from .pqops import (CNOT, CZ, Rot, QubitUnitary, BasisState)
from ._version import __version__

log.getLogger()


projectq_operation_map = {
    #native PennyLane operations also native to ProjectQ
    'PauliX': XGate,
    'PauliY': YGate,
    'PauliZ': ZGate,
    'CNOT': CNOT,
    'CZ': CZ,
    'SWAP': SwapGate,
    'RX': Rx,
    'RY': Ry,
    'RZ': Rz,
    'PhaseShift': R,
    'Hadamard': HGate,
    #operations not natively implemented in ProjectQ but provided in pqops.py
    'Rot': Rot,
    'QubitUnitary': QubitUnitary,
    'BasisState': BasisState,
    #additional operations not native to PennyLane but present in ProjectQ
    'S': SGate,
    'T': TGate,
    'SqrtX': SqrtXGate,
    'SqrtSwap': SqrtSwapGate,
    #operations/expectations of ProjectQ that do not work with PennyLane
    #'AllPauliZ': AllZGate, #todo: enable in case multiple return values per expectation are supported in the future
    #operations/expectations of PennyLane that do not work with ProjectQ
    #'QubitStateVector': StatePreparation,
}

class _ProjectQDevice(Device):
    """ProjectQ device for PennyLane.

    Args:
       wires (int): The number of qubits of the device.

    Keyword Args for Simulator backend:
      gate_fusion (bool): If True, operations are cached and only executed once a certain number of operations has been reached (only has an effect for the c++ simulator).
      rnd_seed (int): Random seed (uses random.randint(0, 4294967295) by default).

    Keyword Args for IBMBackend backend:
      use_hardware (bool): If True, the code is run on the IBM quantum chip (instead of using the IBM simulator)
      num_runs (int): Number of runs to collect statistics (default is 1024). Is equivalent to but takes preference over the shots parameter.
      verbose (bool): If True, statistics are printed, in addition to the measurement result being registered (at the end of the circuit).
      user (string): IBM Quantum Experience user name
      password (string): IBM Quantum Experience password
      device (string): Device to use (e.g., ‘ibmqx4’ or ‘ibmqx5’) if use_hardware is set to True. Default is ibmqx4.
      retrieve_execution (int): Job ID to retrieve instead of re-running the circuit (e.g., if previous run timed out).
    """
    name = 'ProjectQ PennyLane plugin'
    short_name = 'projectq'
    pennylane_requires = '0.1.0'
    version = '0.1.0'
    plugin_version = __version__
    author = 'Christian Gogolin'
    _capabilities = {'backend': list(["Simulator", "ClassicalSimulator", "IBMBackend"])}

    def __init__(self, wires, *, shots=0, **kwargs):
        super().__init__(wires=wires, shots=shots)

        # translate some aguments
        for k, v in {'log':'verbose'}.items():
            if k in kwargs:
                kwargs[v] = kwargs[k]

        # clean some arguments
        if 'num_runs' in kwargs and isinstance(kwargs['num_runs'], int) and kwargs['num_runs'] > 0:
            self.shots = kwargs['num_runs']
        else:
            kwargs['num_runs'] = self.shots

        self.backend = kwargs['backend']
        del kwargs['backend']
        self.kwargs = kwargs
        self.eng = None
        self.reg = None
        self.first_operation = True
        self.reset() #the actual initialization is done in reset()

    def reset(self):
        self.reg = self.eng.allocate_qureg(self.num_wires)
        self.first_operation = True

    def __repr__(self):
        return super().__repr__() +'Backend: ' +self.backend +'\n'

    def __str__(self):
        return super().__str__() +'Backend: ' +self.backend +'\n'

    def post_expval(self):
        self._deallocate()

    def apply(self, operation, wires, par):
        operation = self._operation_map[operation](*par)
        if isinstance(operation, BasisState) and not self.first_operation:
            raise DeviceError("Operation {} cannot be used after other Operations have already been applied on a {} device.".format(operation, self.short_name))
        self.first_operation = False

        qureg = [self.reg[i] for i in wires]
        if isinstance(operation, (pq.ops._metagates.ControlledGate, pq.ops._gates.SqrtSwapGate, pq.ops._gates.SwapGate)):
            qureg = tuple(qureg)
        operation | qureg #pylint: disable=pointless-statement

    def _deallocate(self):
        """Deallocate all qubits to make ProjectQ happy

        See also: https://github.com/ProjectQ-Framework/ProjectQ/issues/2

        Drawback: This is probably rather resource intensive.
        """
        if self.eng is not None and self.backend == 'Simulator':
            pq.ops.All(pq.ops.Measure) | self.reg #avoid an unfriendly error message: https://github.com/ProjectQ-Framework/ProjectQ/issues/2

    def filter_kwargs_for_backend(self, kwargs):
        return {key:value for key, value in kwargs.items() if key in self._backend_kwargs}

    @property
    def operations(self):
        """Get the supported set of operations.

        Returns:
            set[str]: the set of PennyLane operation names the device supports
        """
        return set(self._operation_map.keys())

    @property
    def expectations(self):
        """Get the supported set of expectations.

        Returns:
            set[str]: the set of PennyLane expectation names the device supports
        """
        return set(self._expectation_map.keys())



class ProjectQSimulator(_ProjectQDevice):
    """A PennyLane :code:`projectq.simulator` device for the `ProjectQ Simulator <https://projectq.readthedocs.io/en/latest/projectq.backends.html#projectq.backends.Simulator>`_ backend.

    Args:
       wires (int): The number of qubits of the device

    Keyword Args:
      gate_fusion (bool): If True, operations are cached and only executed once a certain number of operations has been reached (only has an effect for the c++ simulator).
      rnd_seed (int): Random seed (uses random.randint(0, 4294967295) by default).

    This device can, for example, be instantiated from PennyLane as follows:

    .. code-block:: python

        import pennylane as qml
        dev = qml.device('projectq.simulator', wires=XXX)

    Supported PennyLane Operations:
      :class:`pennylane.PauliX`,
      :class:`pennylane.PauliY`,
      :class:`pennylane.PauliZ`,
      :class:`pennylane.CNOT`,
      :class:`pennylane.CZ`,
      :class:`pennylane.SWAP`,
      :class:`pennylane.RX`,
      :class:`pennylane.RY`,
      :class:`pennylane.RZ`,
      :class:`pennylane.PhaseShift`,
      :class:`pennylane.QubitStateVector`,
      :class:`pennylane.Hadamard`,
      :class:`pennylane.Rot`,
      :class:`pennylane.QubitUnitary`,
      :class:`pennylane.BasisState`

    Supported PennyLane Expectations:
      :class:`pennylane.PauliX`,
      :class:`pennylane.PauliY`,
      :class:`pennylane.PauliZ`

    Extra Operations:
      :class:`pennylane_pq.S <pennylane_pq.ops.S>`,
      :class:`pennylane_pq.S <pennylane_pq.ops.S>`,
      :class:`pennylane_pq.T <pennylane_pq.ops.T>`,
      :class:`pennylane_pq.SqrtX <pennylane_pq.ops.SqrtX>`,
      :class:`pennylane_pq.SqrtSwap <pennylane_pq.ops.SqrtSwap>`

    ..
       :class:`pennylane_pq.AllPauliZ <pennylane_pq.ops.AllPauliZ>`

       Extra Expectations:
         :class:`pennylane_pq.expval.AllPauliZ`

    """

    short_name = 'projectq.simulator'
    _operation_map = projectq_operation_map
    _expectation_map = {key:val for key, val in _operation_map.items() if val in [XGate, YGate, ZGate]}
    _circuits = {}
    _backend_kwargs = ['gate_fusion', 'rnd_seed']

    def __init__(self, wires, **kwargs):
        kwargs['backend'] = 'Simulator'
        super().__init__(wires, **kwargs)

    def reset(self):
        backend = pq.backends.Simulator(**self.filter_kwargs_for_backend(self.kwargs))
        self.eng = pq.MainEngine(backend)
        super().reset()

    def pre_expval(self):
        self.eng.flush(deallocate_qubits=False)

    def expval(self, expectation, wires, par):
        if expectation == 'PauliX' or expectation == 'PauliY' or expectation == 'PauliZ':
            if isinstance(wires, int):
                wire = wires
            else:
                wire = wires[0]

            ev = self.eng.backend.get_expectation_value(pq.ops.QubitOperator(str(expectation)[-1]+'0'), [self.reg[wire]])
            #variance = 1 - ev**2
        # elif expectation == 'AllPauliZ':
        #      ev = [ self.eng.backend.get_expectation_value(pq.ops.QubitOperator("Z"+'0'), [qubit]) for qubit in self.reg]
        #      #variance = [1 - e**2 for e in ev]

        return ev

class ProjectQIBMBackend(_ProjectQDevice):
    """A PennyLane :code:`projectq.ibm` device for the `ProjectQ IBMBackend <https://projectq.readthedocs.io/en/latest/projectq.backends.html#projectq.backends.IBMBackend>`_ backend.

    .. note:: This device computes expectation values by averaging over a finite number of runs of the quantum circuit. Irrespective of whether this is done on real quantum hardware, or on the IBM simulator, this means that expectation values (and therefore also gradients) will have a finite accuracy and fluctuate from run to run.

    Args:
       wires (int): The number of qubits of the device

    Keyword Args:
      use_hardware (bool): If True, the code is run on the IBM quantum chip (instead of using the IBM simulator)
      num_runs (int): Number of runs to collect statistics (default is 1024). Is equivalent to but takes preference over the shots parameter.
      verbose (bool): If True, statistics are printed, in addition to the measurement result being registered (at the end of the circuit)
      user (string): IBM Quantum Experience user name
      password (string): IBM Quantum Experience password
      device (string): Device to use (‘ibmqx4’, or ‘ibmqx5’) if :code:`use_hardware` is set to True. Default is 'ibmqx4'.
      retrieve_execution (int): Job ID to retrieve instead of re-running the circuit (e.g., if previous run timed out)
    This device can, for example, be instantiated from PennyLane as follows:

    .. code-block:: python

        import pennylane as qml
        dev = qml.device('projectq.ibm', wires=XXX, user="XXX", password="XXX")

    .. note:: To avoid leaking your user name and password when sharing code, it is better to specify the user name and password in your `PennyLane configuration file <https://pennylane.readthedocs.io/en/latest/code/configuration.html>`_.

    Supported PennyLane Operations:
      :class:`pennylane.PauliX`,
      :class:`pennylane.PauliY`,
      :class:`pennylane.PauliZ`,
      :class:`pennylane.CNOT`,
      :class:`pennylane.CZ`,
      :class:`pennylane.SWAP`,
      :class:`pennylane.RX`,
      :class:`pennylane.RY`,
      :class:`pennylane.RZ`,
      :class:`pennylane.PhaseShift`,
      :class:`pennylane.QubitStateVector`,
      :class:`pennylane.Hadamard`,
      :class:`pennylane.Rot`,
      :class:`pennylane.BasisState`

    Supported PennyLane Expectations:
      :class:`pennylane.PauliX`,
      :class:`pennylane.PauliY`,
      :class:`pennylane.PauliZ`

    Extra Operations:
      :class:`pennylane_pq.S <pennylane_pq.ops.S>`,
      :class:`pennylane_pq.T <pennylane_pq.ops.T>`,
      :class:`pennylane_pq.SqrtX <pennylane_pq.ops.SqrtX>`,
      :class:`pennylane_pq.SqrtSwap <pennylane_pq.ops.SqrtSwap>`,

    ..
       :class:`pennylane_pq.AllPauliZ <pennylane_pq.ops.AllPauliZ>`

       Extra Expectations:
         :class:`pennylane_pq.expval.AllPauliZ`
    """

    short_name = 'projectq.ibm'
    _operation_map = {key:val for key, val in projectq_operation_map.items() if val in [HGate, XGate, YGate, ZGate, SGate, TGate, SqrtXGate, SwapGate, Rx, Ry, Rz, R, CNOT, CZ, Rot, BasisState]}
    _expectation_map = {key:val for key, val in _operation_map.items() if val in [ZGate]}
    _circuits = {}
    _backend_kwargs = ['use_hardware', 'num_runs', 'verbose', 'user', 'password', 'device', 'retrieve_execution']

    def __init__(self, wires, **kwargs):
        # check that necessary arguments are given
        if 'user' not in kwargs:
            raise ValueError('An IBM Quantum Experience user name specified via the "user" keyword argument is required')
        if 'password' not in kwargs:
            raise ValueError('An IBM Quantum Experience password specified via the "password" keyword argument is required')

        import projectq.setups.ibm

        kwargs['backend'] = 'IBMBackend'
        super().__init__(wires, **kwargs)

    def reset(self):
        backend = pq.backends.IBMBackend(**self.filter_kwargs_for_backend(self.kwargs))
        self.eng = pq.MainEngine(backend, engine_list=pq.setups.ibm.get_engine_list())
        super().reset()

    def pre_expval(self):
        pq.ops.All(pq.ops.Measure) | self.reg
        self.eng.flush()

    def expval(self, expectation, wires, par):
        probabilities = self.eng.backend.get_probabilities(self.reg)

        if expectation == 'PauliZ':
            if isinstance(wires, int):
                wire = wires
            else:
                wire = wires[0]

            ev = (1-(2*sum(p for (state, p) in probabilities.items() if state[wire] == '1'))-(1-2*sum(p for (state, p) in probabilities.items() if state[wire] == '0')))/2
            #variance = 1 - ev**2
        # elif expectation == 'AllPauliZ':
        #     ev = [ ((1-2*sum(p for (state,p) in probabilities.items() if state[i] == '1'))-(1-2*sum(p for (state,p) in probabilities.items() if state[i] == '0')))/2 for i in range(len(self.reg)) ]
        #     #variance = [1 - e**2 for e in ev]

        return ev

class ProjectQClassicalSimulator(_ProjectQDevice):
    """A PennyLane :code:`projectq.classical` device for the `ProjectQ ClassicalSimulator <https://projectq.readthedocs.io/en/latest/projectq.backends.html#projectq.backends.ClassicalSimulator>`_ backend.

    Args:
       wires (int): The number of qubits of the device

    This device can, for example, be instantiated from PennyLane as follows:

    .. code-block:: python

        import pennylane as qml
        dev = qml.device('projectq.classical', wires=XXX)

    Supported PennyLane Operations:
      :class:`pennylane.PauliX`,
      :class:`pennylane.CNOT`

    Supported PennyLane Expectations:
      :class:`pennylane.PauliZ`

    ..
       Extra Operations:
         :class:`pennylane_pq.AllPauliZ <pennylane_pq.ops.AllPauliZ>`

       Extra Expectations:
         :class:`pennylane_pq.expval.AllPauliZ`
    """

    short_name = 'projectq.classical'
    _operation_map = {key:val for key, val in projectq_operation_map.items() if val in [XGate, CNOT]}
    _expectation_map = {key:val for key, val in projectq_operation_map.items() if val in [ZGate]}
    _circuits = {}
    _backend_kwargs = []

    def __init__(self, wires, **kwargs):
        kwargs['backend'] = 'ClassicalSimulator'
        super().__init__(wires, **kwargs)

    def reset(self):
        backend = pq.backends.ClassicalSimulator(**self.filter_kwargs_for_backend(self.kwargs))
        self.eng = pq.MainEngine(backend)
        super().reset()

    def pre_expval(self):
        pq.ops.All(pq.ops.Measure) | self.reg
        self.eng.flush()

    def expval(self, expectation, wires, par):
        if expectation == 'PauliZ':
            if isinstance(wires, int):
                wire = wires
            else:
                wire = wires[0]

            ev = 1 - 2*int(self.reg[wire])
            #variance = 1 - ev**2
        # elif expectation == 'AllPauliZ':
        #     ev = [ 1 - 2*int(self.reg[wire]) for wire in self.reg]
        #     #variance = [1 - e**2 for e in ev]

        return ev
