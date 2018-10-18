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
r"""
Devices
=======

.. currentmodule:: openqml_pq.devices

This plugin offers access to the following ProjectQ backends by providing corresponding OpenQML devices:

.. autosummary::
   :nosignatures:

   ProjectQSimulator
   ProjectQIBMBackend
   ProjectQClassicalSimulator

.. todo::
   Is there a way to do generate the following documentation more automatically?

.. todo::
   Is there a nice way to link to the documentation of the OpenQML native Operations/Expectations?

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
import numpy as np
from openqml import Device, DeviceError

import projectq as pq

from projectq.ops import (HGate, XGate, YGate, ZGate, SGate, TGate, SqrtXGate, SwapGate, SqrtSwapGate, Rx, Ry, Rz, R, Ph, StatePreparation, SGate, TGate, SqrtXGate, SqrtSwapGate)
from .pqops import (CNOT, CZ, Toffoli, AllZGate, Rot, QubitUnitary, BasisState)

from ._version import __version__


projectq_operation_map = {
    #native OpenQML operations also native to ProjectQ
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
    #additional operations not native to OpenQML but present in ProjectQ
    'S': SGate,
    'T': TGate,
    'SqrtX': SqrtXGate,
    'SqrtSwap': SqrtSwapGate,
    #operations/expectations of ProjectQ that do work with OpenQML
#    'AllPauliZ': AllZGate, #todo: enable once https://github.com/XanaduAI/openqml/issues/61 is resolved
    #operations/expectations of OpenQML that do work with ProjectQ
#    'QubitStateVector': StatePreparation,
}

class _ProjectQDevice(Device):
    """ProjectQ device for OpenQML.

    Args:
       wires (int): The number of qubits of the device.

    Keyword Args for Simulator backend:
      gate_fusion (bool): If True, gates are cached and only executed once a certain gate-size has been reached (only has an effect for the c++ simulator).
      rnd_seed (int): Random seed (uses random.randint(0, 4294967295) by default).

    Keyword Args for IBMBackend backend:
      use_hardware (bool): If True, the code is run on the IBM quantum chip (instead of using the IBM simulator)
      num_runs (int): Number of runs to collect statistics. (default is 1024)
      verbose (bool): If True, statistics are printed, in addition to the measurement result being registered (at the end of the circuit).
      user (string): IBM Quantum Experience user name
      password (string): IBM Quantum Experience password
      device (string): Device to use (‘ibmqx4’, or ‘ibmqx5’) if use_hardware is set to True. Default is ibmqx4.
      retrieve_execution (int): Job ID to retrieve instead of re-running the circuit (e.g., if previous run timed out).
    """
    name = 'ProjectQ OpenQML plugin'
    short_name = 'projectq'
    api_version = '0.1.0'
    plugin_version = __version__
    author = 'Christian Gogolin'
    _capabilities = {'backend': list(["Simulator", "ClassicalSimulator", "IBMBackend"])}

    def __init__(self, wires, *, shots=0, **kwargs):
        super().__init__(self.short_name, wires=wires, shots=shots)

        # translate some aguments
        for k,v in {'log':'verbose'}.items():
            if k in kwargs:
                kwargs.setdefault(v, kwargs[k])

        # clean some arguments
        if 'num_runs' in kwargs:
            if isinstance(kwargs['num_runs'], int) and kwargs['num_runs']>0:
                self.n_eval = kwargs['num_runs']
            else:
                self.n_eval = 0
                del(kwargs['num_runs'])

        self.backend = kwargs['backend']
        del(kwargs['backend'])
        self.kwargs = kwargs
        self.eng = None
        self.reg = None
        self.reset() #the actual initialization is done in reset()

    def reset(self):
        self.reg = self.eng.allocate_qureg(self.num_wires)

    def __repr__(self):
        return super().__repr__() +'Backend: ' +self.backend +'\n'

    def __str__(self):
        return super().__str__() +'Backend: ' +self.backend +'\n'

    def post_expval(self):
        self._deallocate()

    def apply(self, gate_name, wires, par):
        gate = self._operation_map[gate_name](*par)
        list = [self.reg[i] for i in wires]
        if not isinstance(gate, pq.ops._metagates.Tensor):
            gate | tuple(list) #pylint: disable=pointless-statement
        else:
            gate | list #pylint: disable=pointless-statement

    def _deallocate(self):
        """Deallocate all qubits to make ProjectQ happy

        See also: https://github.com/ProjectQ-Framework/ProjectQ/issues/2

        Drawback: This is probably rather resource intensive.
        """
        if self.eng is not None and self.backend == 'Simulator':
            pq.ops.All(pq.ops.Measure) | self.reg #avoid an unfriendly error message: https://github.com/ProjectQ-Framework/ProjectQ/issues/2

    def filter_kwargs_for_backend(self, kwargs):
        return { key:value for key,value in kwargs.items() if key in self._backend_kwargs }


class ProjectQSimulator(_ProjectQDevice):
    """An OpenQML device for the `ProjectQ Simulator <https://projectq.readthedocs.io/en/latest/projectq.backends.html#projectq.backends.Simulator>`_ backend.

    Args:
       wires (int): The number of qubits of the device

    Keyword Args:
      gate_fusion (bool): If True, gates are cached and only executed once a certain gate-size has been reached (only has an effect for the C++ simulator)
      rnd_seed (int): Random seed (uses random.randint(0, 4294967295) by default)

    This device can, for example, be instantiated from OpenQML as follows:

    .. code-block:: python

        import openqml as qm
        dev = qm.device('projectq.simulator', wires=XXX)

    .. todo:: update these links to main library

    Supported OpenQML Operations:
      :class:`openqml.PauliX`,
      :class:`openqml.PauliY`,
      :class:`openqml.PauliZ`,
      :class:`openqml.CNOT`,
      :class:`openqml.CZ`,
      :class:`openqml.SWAP`,
      :class:`openqml.RX`,
      :class:`openqml.RY`,
      :class:`openqml.RZ`,
      :class:`openqml.PhaseShift`,
      :class:`openqml.QubitStateVector`,
      :class:`openqml.Hadamard`,
      :class:`openqml.Rot`,
      :class:`openqml.QubitUnitary`

    Supported OpenQML Expectations:
      :class:`openqml.PauliX`,
      :class:`openqml.PauliY`,
      :class:`openqml.PauliZ`

    .. todo:: do we want to update these to be available at top level of openqml_pq, as in the main library?

    Extra Operations:
      :class:`openqml_pq.ops.S`,
      :class:`openqml_pq.ops.T`,
      :class:`openqml_pq.ops.SqrtX`,
      :class:`openqml_pq.ops.SqrtSwap`,
      :class:`openqml_pq.ops.AllPauliZ`

    Extra Expectations:
      :class:`openqml_pq.expval.AllPauliZ`
    """

    short_name = 'projectq.simulator'
    _operation_map = projectq_operation_map
    _expectation_map = {key:val for key, val in _operation_map.items() if val in [XGate, YGate, ZGate, AllZGate]}
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
        elif expectation == 'AllPauliZ':
             ev = [ self.eng.backend.get_expectation_value(pq.ops.QubitOperator("Z"+'0'), [qubit]) for qubit in self.reg]
             #variance = [1 - e**2 for e in ev]
        else:
            raise DeviceError("Observable {} not supported by {}".format(expectation, self.name))

        return ev

class ProjectQIBMBackend(_ProjectQDevice):
    """An OpenQML device for the `ProjectQ IBMBackend <https://projectq.readthedocs.io/en/latest/projectq.backends.html#projectq.backends.IBMBackend>`_ backend.

    Args:
       wires (int): The number of qubits of the device

    Keyword Args:
      use_hardware (bool): If True, the code is run on the IBM quantum chip (instead of using the IBM simulator)
      num_runs (int): Number of runs to collect statistics (default is 1024)
      verbose (bool): If True, statistics are printed, in addition to the measurement result being registered (at the end of the circuit)
      user (string): IBM Quantum Experience user name
      password (string): IBM Quantum Experience password
      device (string): Device to use (‘ibmqx4’, or ‘ibmqx5’) if :code:`use_hardware` is set to True. Default is 'ibmqx4'.
      retrieve_execution (int): Job ID to retrieve instead of re-running the circuit (e.g., if previous run timed out)
    This device can, for example, be instantiated from OpenQML as follows:

    .. code-block:: python

        import openqml as qm
        dev = qm.device('projectq.ibm', wires=XXX, user="XXX", password="XXX")

    .. todo:: update these links to main library

    Supported OpenQML Operations:
      :class:`openqml.PauliX`,
      :class:`openqml.PauliY`,
      :class:`openqml.PauliZ`,
      :class:`openqml.CNOT`,
      :class:`openqml.CZ`,
      :class:`openqml.SWAP`,
      :class:`openqml.RX`,
      :class:`openqml.RY`,
      :class:`openqml.RZ`,
      :class:`openqml.PhaseShift`,
      :class:`openqml.QubitStateVector`,
      :class:`openqml.Hadamard`,
      :class:`openqml.Rot`,
      :class:`openqml.QubitUnitary`

    Supported OpenQML Expectations:
      :class:`openqml.PauliX`,
      :class:`openqml.PauliY`,
      :class:`openqml.PauliZ`

    .. todo:: do we want to update these to be available at top level of openqml_pq, as in the main library?

    Extra Operations:
      :class:`openqml_pq.ops.S`,
      :class:`openqml_pq.ops.T`,
      :class:`openqml_pq.ops.SqrtX`,
      :class:`openqml_pq.ops.SqrtSwap`,
      :class:`openqml_pq.ops.AllPauliZ`

    Extra Expectations:
      :class:`openqml_pq.expval.AllPauliZ`
    """

    short_name = 'projectq.ibmbackend'
    _operation_map = {key:val for key, val in projectq_operation_map.items() if val in [HGate, XGate, YGate, ZGate, SGate, TGate, SqrtXGate, SwapGate, Rx, Ry, Rz, R, CNOT, CZ]}
    _expectation_map = {key:val for key, val in _operation_map.items() if val in [ZGate, AllZGate]}
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

    def pre_expvals(self):
        pq.ops.All(pq.ops.Measure) | self.reg
        self.eng.flush()

    def expval(self, expectation, wires, par):
        probabilities = self.eng.backend.get_probabilities(self.reg)

        if expectation == 'PauliZ':
            if isinstance(wires, int):
                wire = wires
            else:
                wire = wires[0]

            ev = ((2*sum(p for (state,p) in probabilities.items() if state[wire] == '1')-1)-(2*sum(p for (state,p) in probabilities.items() if state[wire] == '0')-1))
            #variance = 1 - ev**2
        elif expectation == 'AllPauliZ':
            ev = [ ((2*sum(p for (state,p) in probabilities.items() if state[i] == '1')-1)-(2*sum(p for (state,p) in probabilities.items() if state[i] == '0')-1)) for i in range(len(self.reg)) ]
            #variance = [1 - e**2 for e in ev]
        else:
            raise DeviceError("Observable {} not supported by {}".format(expectation, self.name))

        return ev

class ProjectQClassicalSimulator(_ProjectQDevice):
    """An OpenQML device for the `ProjectQ ClassicalSimulator <https://projectq.readthedocs.io/en/latest/projectq.backends.html#projectq.backends.ClassicalSimulator>`_ backend.

    Args:
       wires (int): The number of qubits of the device

    This device can, for example, be instantiated from OpenQML as follows:

    .. code-block:: python

        import openqml as qm
        dev = qm.device('projectq.classical', wires=XXX)

    Supported OpenQML Operations:
      :class:`openqml.PauliX`

    Supported OpenQML Expectations:
      :class:`openqml.PauliZ`

    Extra Operations:
      :class:`openqml_pq.ops.AllPauliZ`

    Extra Expectations:
      :class:`openqml_pq.expval.AllPauliZ`
    """

    short_name = 'projectq.classicalsimulator'
    _operation_map = {key:val for key, val in projectq_operation_map.items() if val in [XGate, CNOT]}
    _expectation_map = {key:val for key, val in _operation_map.items() if val in [ZGate, AllZGate]}
    _circuits = {}
    _backend_kwargs = []

    def __init__(self, wires, **kwargs):
        kwargs['backend'] = 'ClassicalSimulator'
        super().__init__(wires, **kwargs)

    def reset(self):
        backend = pq.backends.ClassicalSimulator(**self.filter_kwargs_for_backend(self.kwargs))
        self.eng = pq.MainEngine(backend)
        super().reset()
