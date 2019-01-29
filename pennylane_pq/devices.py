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

This plugin offers access to the following ProjectQ backends by providing
corresponding PennyLane devices:

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
import abc
import numpy as np
import projectq as pq
from projectq.ops import (HGate, XGate, YGate, ZGate, SGate, TGate, SqrtXGate,
                          SwapGate, Rx, Ry, Rz, R, SqrtSwapGate)

from pennylane import Device, DeviceError

from .pqops import (CNOT, CZ, Rot, QubitUnitary, BasisState)

from ._version import __version__


PROJECTQ_OPERATION_MAP = {
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
    #'AllPauliZ': AllZGate, #todo: enable when multiple return values are supported
    #operations/expectations of PennyLane that do not work with ProjectQ
    #'QubitStateVector': StatePreparation,
    #In addition we support the Identity Expectation, but only as an expectation and not as an Operation, which is we we don't put it here.
}

class _ProjectQDevice(Device): #pylint: disable=abstract-method
    """ProjectQ device for PennyLane.

    Args:
      wires (int): The number of qubits of the device. Default 1 if not specified.
      shots (int): number of circuit evaluations/random samples used to estimate
        expectation values of observables. For simulator devices, a value of 0 (default)
        results in the exact expectation value being returned. For the IBMBackend the
        default is 1024.

    Keyword Args:
      backend (string): Name of the backend, i.e., either "Simulator",
         "ClassicalSimulator", or "IBMBackend".
      verbose (bool): If True, log messages are printed and exceptions are more verbose.

    Keyword Args for Simulator backend:
      gate_fusion (bool): If True, operations are cached and only executed once a
        certain number of operations has been reached (only has an effect for the c++ simulator).
      rnd_seed (int): Random seed (uses random.randint(0, 4294967295) by default).

    Keyword Args for IBMBackend backend:
      use_hardware (bool): If True, the code is run on the IBM quantum chip (instead of using
        the IBM simulator)
      num_runs (int): Number of runs to collect statistics (default is 1024). Is equivalent
        to but takes preference over the shots parameter.
      user (string): IBM Quantum Experience user name
      password (string): IBM Quantum Experience password
      device (string): Device to use (e.g., ‘ibmqx4’ or ‘ibmqx5’) if use_hardware is set to
        True. Default is ibmqx4.
        retrieve_execution (int): Job ID to retrieve instead of re-running the circuit
        (e.g., if previous run timed out).
    """
    name = 'ProjectQ PennyLane plugin'
    short_name = 'projectq'
    pennylane_requires = '0.2.0'
    version = '0.2.0'
    plugin_version = __version__
    author = 'Christian Gogolin'
    _capabilities = {'backend': list(["Simulator", "ClassicalSimulator", "IBMBackend"])}

    @abc.abstractproperty
    def _operation_map(self):
        raise NotImplementedError

    @abc.abstractproperty
    def _expectation_map(self):
        raise NotImplementedError

    @abc.abstractproperty
    def _backend_kwargs(self):
        raise NotImplementedError

    def __init__(self, wires=1, shots=0, *, backend, **kwargs):
        # overwrite shots with num_runs if given
        if 'num_runs' in kwargs:
            shots = kwargs['num_runs']
            del kwargs['num_runs']

        super().__init__(wires=wires, shots=shots)

        if 'verbose' not in kwargs:
            kwargs['verbose'] = False

        self._backend = backend
        self._kwargs = kwargs
        self._eng = None
        self._reg = None
        self._first_operation = True
        self.reset() #the actual initialization is done in reset()

    def reset(self):
        """Reset/initialize the device by allocating qubits.
        """
        self._reg = self._eng.allocate_qureg(self.num_wires)
        self._first_operation = True

    def __repr__(self):
        return super().__repr__() +'Backend: ' +self._backend +'\n'

    def __str__(self):
        return super().__str__() +'Backend: ' +self._backend +'\n'

    def post_expval(self):
        """Deallocate the qubits after expectation values have been retrieved.
        """
        self._deallocate()

    def apply(self, operation, wires, par):
        """Apply a quantum operation.

        For plugin developers: this function should apply the operation on the device.

        Args:
            operation (str): name of the operation
            wires (Sequence[int]): subsystems the operation is applied on
            par (tuple): parameters for the operation
        """
        operation = self._operation_map[operation](*par)
        if isinstance(operation, BasisState) and not self._first_operation:
            raise DeviceError("Operation {} cannot be used after other Operations have already been applied on a {} device.".format(operation, self.short_name)) #pylint: disable=line-too-long
        self._first_operation = False

        qureg = [self._reg[i] for i in wires]
        if isinstance(operation, (pq.ops._metagates.ControlledGate, #pylint: disable=protected-access
                                  pq.ops._gates.SqrtSwapGate, #pylint: disable=protected-access
                                  pq.ops._gates.SwapGate)): #pylint: disable=protected-access
            qureg = tuple(qureg)
        operation | qureg #pylint: disable=pointless-statement

    def _deallocate(self):
        """Deallocate all qubits to make ProjectQ happy

        See also: https://github.com/ProjectQ-Framework/ProjectQ/issues/2

        Drawback: This is probably rather resource intensive.
        """
        if self._eng is not None and self._backend == 'Simulator':
            #avoid an "unfriendly error message":
            #https://github.com/ProjectQ-Framework/ProjectQ/issues/2
            pq.ops.All(pq.ops.Measure) | self._reg #pylint: disable=expression-not-assigned

    def filter_kwargs_for_backend(self, kwargs):
        """Filter the given kwargs for those relevant for the respective device/backend.
        """
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
    """A PennyLane :code:`projectq.simulator` device for the `ProjectQ Simulator
    <https://projectq.readthedocs.io/en/latest/projectq.backends.html#projectq.backends.Simulator>`_
    backend.

    Args:
       wires (int): The number of qubits of the device. Default 1 if not specified.
       shots (int): number of random samples used to estimate expectation values of
         observables. A value of 0 (default) results in the exact expectation value
         being returned.

    Keyword Args:
      gate_fusion (bool): If True, operations are cached and only executed once a
        certain number of operations has been reached (only has an effect for the c++ simulator).
      rnd_seed (int): Random seed (uses random.randint(0, 4294967295) by default).
      verbose (bool): If True, log messages are printed and exceptions are more verbose.

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
      :class:`pennylane.Hadamard`,
      :class:`pennylane.Rot`,
      :class:`pennylane.QubitUnitary`,
      :class:`pennylane.BasisState`

    Supported PennyLane Expectations:
      :class:`pennylane.expval.PauliX`,
      :class:`pennylane.expval.PauliY`,
      :class:`pennylane.expval.PauliZ`,
      :class:`pennylane.expval.Hadamard`,
      :class:`pennylane.expval.Identity`

    Extra Operations:
      :class:`pennylane_pq.S <pennylane_pq.ops.S>`,
      :class:`pennylane_pq.S <pennylane_pq.ops.S>`,
      :class:`pennylane_pq.T <pennylane_pq.ops.T>`,
      :class:`pennylane_pq.SqrtX <pennylane_pq.ops.SqrtX>`,
      :class:`pennylane_pq.SqrtSwap <pennylane_pq.ops.SqrtSwap>`

    """

    short_name = 'projectq.simulator'
    _operation_map = PROJECTQ_OPERATION_MAP
    _expectation_map = dict({key:val for key, val in _operation_map.items()
                             if val in [XGate, YGate, ZGate, HGate]}, **{'Identity': None})
    _circuits = {}
    _backend_kwargs = ['gate_fusion', 'rnd_seed']

    def __init__(self, wires=1, shots=0, **kwargs):
        kwargs['backend'] = 'Simulator'
        super().__init__(wires=wires, shots=shots, **kwargs)

    def reset(self):
        """Reset/initialize the device by initializing the backend and engine, and allocating qubits.
        """
        backend = pq.backends.Simulator(**self.filter_kwargs_for_backend(self._kwargs))
        self._eng = pq.MainEngine(backend, verbose=self._kwargs['verbose'])
        super().reset()

    def pre_expval(self):
        """Flush the device before retrieving expectation values.
        """
        self._eng.flush(deallocate_qubits=False)

    def expval(self, expectation, wires, par):
        """Retrieve the requested expectation value.
        """
        if expectation == 'PauliX' or expectation == 'PauliY' or expectation == 'PauliZ':
            expval = self._eng.backend.get_expectation_value(
                pq.ops.QubitOperator(str(expectation)[-1]+'0'),
                [self._reg[wires[0]]])
            # variance = 1 - expval**2
        elif expectation == 'Hadamard':
            expval = self._eng.backend.get_expectation_value(
                1/np.sqrt(2)*pq.ops.QubitOperator('X0')+1/np.sqrt(2)*pq.ops.QubitOperator('Z0'),
                [self._reg[wires[0]]])
            # variance = 1 - expval**2
        elif expectation == 'Identity':
            expval = 1
            # variance = 1 - expval**2
        # elif expectation == 'AllPauliZ':
        #     expval = [self._eng.backend.get_expectation_value(
        #         pq.ops.QubitOperator("Z"+'0'), [qubit])
        #                for qubit in self._reg]
        #     variance = [1 - e**2 for e in expval]

        if self.shots != 0 and expectation != 'Identity':
            p0 = (expval+1)/2
            n0 = np.random.binomial(self.shots, p0)
            expval = (n0 - (self.shots-n0)) / self.shots

        return expval

class ProjectQIBMBackend(_ProjectQDevice):
    """A PennyLane :code:`projectq.ibm` device for the `ProjectQ IBMBackend
    <https://projectq.readthedocs.io/en/latest/projectq.backends.html#projectq.backends.IBMBackend>`_
    backend.

    .. note::
        This device computes expectation values by averaging over a
        finite number of runs of the quantum circuit. Irrespective of whether
        this is done on real quantum hardware, or on the IBM simulator, this
        means that expectation values (and therefore also gradients) will have
        a finite accuracy and fluctuate from run to run.

    Args:
       wires (int): The number of qubits of the device. Default 1 if not specified.
       shots (int): number of circuit evaluations used to estimate expectation values
         of observables. Default value is 1024.

    Keyword Args:
      use_hardware (bool): If True, the code is run on the IBM quantum chip
        (instead of using the IBM simulator)
      num_runs (int): Number of runs to collect statistics (default is 1024).
        Is equivalent to but takes preference over the shots parameter.
      user (string): IBM Quantum Experience user name
      password (string): IBM Quantum Experience password
      device (string): Device to use (‘ibmqx4’, or ‘ibmqx5’) if
        :code:`use_hardware` is set to True. Default is 'ibmqx4'.
      retrieve_execution (int): Job ID to retrieve instead of re-running
        a circuit (e.g., if previous run timed out).
      verbose (bool): If True, log messages are printed and exceptions are more verbose.

    This device can, for example, be instantiated from PennyLane as follows:

    .. code-block:: python

        import pennylane as qml
        dev = qml.device('projectq.ibm', wires=XXX, user="XXX", password="XXX")

    To avoid leaking your user name and password when sharing code,
    it is better to specify the user name and password in your
    `PennyLane configuration file <https://pennylane.readthedocs.io/configuration.html>`_.

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
      :class:`pennylane.Hadamard`,
      :class:`pennylane.Rot`,
      :class:`pennylane.BasisState`

    Supported PennyLane Expectations:
      :class:`pennylane.expval.PauliX`,
      :class:`pennylane.expval.PauliY`,
      :class:`pennylane.expval.PauliZ`,
      :class:`pennylane.expval.Hadamard`,
      :class:`pennylane.expval.Identity`

    .. note::
       The Expectations :class:`pennylane.expval.PauliY`, :class:`pennylane.expval.PauliZ`,
       and :class:`pennylane.expval.Hadamard`, cannot be natively measured on the
       hardware device. They are implemented by executing a few additional gates on the
       respective wire before the final measurement, which is always performed in the
       :class:`pennylane.expval.PauliZ` basis. These measurements may thus be slightly more
       noisy than native :class:`pennylane.expval.PauliZ` measurement.


    Extra Operations:
      :class:`pennylane_pq.S <pennylane_pq.ops.S>`,
      :class:`pennylane_pq.T <pennylane_pq.ops.T>`,
      :class:`pennylane_pq.SqrtX <pennylane_pq.ops.SqrtX>`,
      :class:`pennylane_pq.SqrtSwap <pennylane_pq.ops.SqrtSwap>`,

    """

    short_name = 'projectq.ibm'
    _operation_map = {key:val for key, val in PROJECTQ_OPERATION_MAP.items()
                      if val in [HGate, XGate, YGate, ZGate, SGate, TGate,
                                 SqrtXGate, SwapGate, SqrtSwapGate, Rx, Ry, Rz, R, CNOT,
                                 CZ, Rot, BasisState]}
    _expectation_map = dict({key:val for key, val in _operation_map.items() if val in [HGate, XGate, YGate, ZGate]}, **{'Identity': None})
    _circuits = {}
    _backend_kwargs = ['use_hardware', 'num_runs', 'verbose', 'user', 'password', 'device',
                       'retrieve_execution']

    def __init__(self, wires=1, shots=1024, **kwargs):
        # check that necessary arguments are given
        if 'user' not in kwargs:
            raise ValueError('An IBM Quantum Experience user name specified via the "user" keyword argument is required') #pylint: disable=line-too-long
        if 'password' not in kwargs:
            raise ValueError('An IBM Quantum Experience password specified via the "password" keyword argument is required') #pylint: disable=line-too-long

        import projectq.setups.ibm #pylint: disable=unused-variable

        kwargs['backend'] = 'IBMBackend'
        super().__init__(wires=wires, shots=shots, **kwargs)

    def reset(self):
        """Reset/initialize the device by initializing the backend and engine, and allocating qubits.
        """
        backend = pq.backends.IBMBackend(num_runs=self.shots, **self.filter_kwargs_for_backend(self._kwargs))
        self._eng = pq.MainEngine(backend, verbose=self._kwargs['verbose'], engine_list=pq.setups.ibm.get_engine_list())
        super().reset()

    def pre_expval(self):
        """Rotate qubits to the right basis before measurement, apply a measure all
        operation and flush the device before retrieving expectation values.
        """
        if hasattr(self, 'expval_queue'): #we raise an except below in case there is no expval_queue but we are asked to measure in a basis different from PauliZ
            for e in self.expval_queue:
                if e.name == 'PauliX':
                    self.apply('Hadamard', e.wires, list())
                elif e.name == 'PauliY':
                    self.apply('PauliZ', e.wires, list())
                    self.apply('S', e.wires, list())
                    self.apply('Hadamard', e.wires, list())
                elif e.name == 'Hadamard':
                    self.apply('RY', e.wires, [-np.pi/4])
                elif e.name == 'Hermitian':
                    raise NotImplementedError

        pq.ops.All(pq.ops.Measure) | self._reg #pylint: disable=expression-not-assigned
        self._eng.flush()

    def expval(self, expectation, wires, par):
        """Retrieve the requested expectation value.
        """
        probabilities = self._eng.backend.get_probabilities(self._reg)

        if expectation == 'PauliX' or expectation == 'PauliY' or expectation == 'PauliZ' or expectation == 'Hadamard':

            if expectation != 'PauliZ' and not hasattr(self, 'expval_queue'):
                raise DeviceError("Measurements in basis other than PauliZ are only supported when this plugin is used with versions of PennyLane that expose the expval_queue. Please update PennyLane and this plugin.")

            expval = (1-(2*sum(p for (state, p) in probabilities.items() if state[wires[0]] == '1'))-(1-2*sum(p for (state, p) in probabilities.items() if state[wires[0]] == '0')))/2
            #variance = 1 - ev**2
        elif expectation == 'Hermitian':
            raise NotImplementedError
        elif expectation == 'Identity':
            expval = sum(p for (state, p) in probabilities.items())
            # variance = 1 - expval**2
        # elif expectation == 'AllPauliZ':
        #     expval = [((1-2*sum(p for (state, p) in probabilities.items()
        #                         if state[i] == '1'))
        #                -(1-2*sum(p for (state, p) in probabilities.items()
        #                          if state[i] == '0')))/2 for i in range(len(self._reg))]
        #     variance = [1 - e**2 for e in expval]

        return expval

class ProjectQClassicalSimulator(_ProjectQDevice):
    """A PennyLane :code:`projectq.classical` device for the `ProjectQ ClassicalSimulator
    <https://projectq.readthedocs.io/en/latest/projectq.backends.html#projectq.backends.ClassicalSimulator>`_
    backend.

    Args:
       wires (int): The number of qubits of the device. Default 1 if not specified.

    Keyword Args:
      verbose (bool): If True, log messages are printed and exceptions are more verbose.

    This device can, for example, be instantiated from PennyLane as follows:

    .. code-block:: python

        import pennylane as qml
        dev = qml.device('projectq.classical', wires=XXX)

    Supported PennyLane Operations:
      :class:`pennylane.PauliX`,
      :class:`pennylane.CNOT`,
      :class:`pennylane.BasisState`

    Supported PennyLane Expectations:
      :class:`pennylane.expval.PauliZ`,
      :class:`pennylane.expval.Identity`

    """

    short_name = 'projectq.classical'
    _operation_map = {key:val for key, val in PROJECTQ_OPERATION_MAP.items()
                      if val in [XGate, CNOT, BasisState]}
    _expectation_map = dict({key:val for key, val in PROJECTQ_OPERATION_MAP.items()
                             if val in [ZGate]}, **{'Identity': None})
    _circuits = {}
    _backend_kwargs = []

    def __init__(self, wires=1, **kwargs):
        kwargs['backend'] = 'ClassicalSimulator'
        super().__init__(wires=wires, shots=0, **kwargs)

    def reset(self):
        """Reset/initialize the device by initializing the backend and engine, and allocating qubits.
        """
        backend = pq.backends.ClassicalSimulator(**self.filter_kwargs_for_backend(self._kwargs))
        self._eng = pq.MainEngine(backend, verbose=self._kwargs['verbose'])
        super().reset()

    def pre_expval(self):
        """Apply a measure all operation and flush the device before retrieving expectation values.
        """
        pq.ops.All(pq.ops.Measure) | self._reg #pylint: disable=expression-not-assigned
        self._eng.flush()

    def expval(self, expectation, wires, par):
        """Retrieve the requested expectation value.
        """
        if expectation == 'PauliZ':
            wire = wires[0]

            expval = 1 - 2*int(self._reg[wire])
            # variance = 1 - expval**2
        elif expectation == 'Identity':
            expval = 1
            # variance = 1 - expval**2
        # elif expectation == 'AllPauliZ':
        #     expval = [ 1 - 2*int(self._reg[wire]) for wire in self._reg]
        #     #variance = [1 - e**2 for e in expval]

        return expval
