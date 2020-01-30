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
Wrapper classes for ProjectQ Operations
===================

.. currentmodule:: pennylane_pq.ops

This module provides wrapper classes for `Operations` that are missing a class in ProjectQ.

"""
import projectq as pq
from projectq.ops import BasicGate, SelfInverseGate
import numpy as np

class BasicProjectQGate(BasicGate): # pylint: disable=too-few-public-methods
    """Base class for ProjectQ gates."""
    def __init__(self, name="unnamed"):
        super().__init__()
        self.name = name

    def __str__(self):
        return self.name

try:
    from projectq.ops import MatrixGate #pylint: disable=ungrouped-imports
except ImportError:
    MatrixGate = BasicGate

class BasicProjectQMatrixGate(MatrixGate): # pylint: disable=too-few-public-methods
    """Base class for ProjectQ gates defined via a matrix."""
    def __init__(self, name="unnamed"):
        super().__init__()
        self.name = name

    def __str__(self):
        return self.name

class CNOT(BasicProjectQGate): # pylint: disable=too-few-public-methods
    """Class for the CNOT gate.

    Contrary to other gates, ProjectQ does not have a class for the CNOT gate,
    as it is implemented as a meta-gate.
    For consistency we define this class, whose constructor is made to retun
    a gate with the correct properties by overwriting __new__().
    """
    def __new__(*par): # pylint: disable=no-method-argument
        return pq.ops.C(pq.ops.XGate())

class CZ(BasicProjectQGate): # pylint: disable=too-few-public-methods
    """Class for the CNOT gate.

    Contrary to other gates, ProjectQ does not have a class for the CZ gate,
    as it is implemented as a meta-gate.
    For consistency we define this class, whose constructor is made to retun
    a gate with the correct properties by overwriting __new__().
    """
    def __new__(*par): # pylint: disable=no-method-argument
        return pq.ops.C(pq.ops.ZGate())

# class Toffoli(BasicProjectQGate): # pylint: disable=too-few-public-methods
#     """Class for the Toffoli gate.

#     Contrary to other gates, ProjectQ does not have a class for the Toffoli gate,
#     as it is implemented as a meta-gate.
#     For consistency we define this class, whose constructor is made to retun
#     a gate with the correct properties by overwriting __new__().
#     """
#     def __new__(*par): # pylint: disable=no-method-argument
#         return pq.ops.C(pq.ops.ZGate(), 2)

# class AllZGate(BasicProjectQGate): # pylint: disable=too-few-public-methods
#     """Class for the AllZ gate.

#     Contrary to other gates, ProjectQ does not have a class for the AllZ gate,
#     as it is implemented as a meta-gate.
#     For consistency we define this class, whose constructor is made to retun
#     a gate with the correct properties by overwriting __new__().
#     """
#     def __new__(*par): # pylint: disable=no-method-argument
#         return pq.ops.Tensor(pq.ops.ZGate())

class Rot(BasicProjectQGate):
    """Class for the arbitrary single qubit rotation gate.

    ProjectQ does not currently have an arbitrary single qubit rotation gate,
    so we provide a class that return a suitable combination of rotation gates
    assembled into a single gate from the constructor of this class.
    """
    def __init__(self, *par):
        BasicProjectQGate.__init__(self, name=self.__class__.__name__)
        self.angles = par

    def __or__(self, qubits):
        pq.ops.Rz(self.angles[0]) | qubits #pylint: disable=expression-not-assigned
        pq.ops.Ry(self.angles[1]) | qubits #pylint: disable=expression-not-assigned
        pq.ops.Rz(self.angles[2]) | qubits #pylint: disable=expression-not-assigned

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.angles == other.angles
        return False

class QubitUnitary(BasicProjectQGate): # pylint: disable=too-few-public-methods
    """Class for the QubitUnitary gate.

    ProjectQ does not currently have a real arbitrary QubitUnitary gate,
    but it allows to directly set the matrix of single qubit gates and
    can then still decompose them into the elementary gates set, so we
    do this here.
    """
    def __new__(*par):
        unitary_gate = BasicProjectQMatrixGate(par[0].__name__)
        unitary_gate.matrix = np.array(par[1])
        return unitary_gate

class BasisState(BasicProjectQGate, SelfInverseGate): # pylint: disable=too-few-public-methods
    """Class for the BasisState preparation.

    ProjectQ does not currently have a dedicated gate for this, so we implement it here.
    """
    def __init__(self, basis_state_to_prep):
        BasicProjectQGate.__init__(self, name=self.__class__.__name__)
        SelfInverseGate.__init__(self)
        self.basis_state_to_prep = basis_state_to_prep

    def __or__(self, qubits):
        for i, qureg in enumerate(qubits):
            if self.basis_state_to_prep[i] == 1:
                pq.ops.XGate() | qureg #pylint: disable=expression-not-assigned

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.basis_state_to_prep == other.basis_state_to_prep
        return False
