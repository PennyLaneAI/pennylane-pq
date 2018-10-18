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
Wrapper classes for ProjectQ Operations
===================

.. currentmodule:: openqml_pq.ops

This module provides wrapper classes for `Operations` that are missing a class in ProjectQ.

"""
import projectq as pq
import numpy as np

class BasicProjectQGate(pq.ops.BasicGate): # pylint: disable=too-few-public-methods
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
        #return pq.ops.C(pq.ops.XGate())
        return pq.ops.C(pq.ops.NOT)


class CZ(BasicProjectQGate): # pylint: disable=too-few-public-methods
    """Class for the CNOT gate.

    Contrary to other gates, ProjectQ does not have a class for the CZ gate,
    as it is implemented as a meta-gate.
    For consistency we define this class, whose constructor is made to retun
    a gate with the correct properties by overwriting __new__().
    """
    def __new__(*par): # pylint: disable=no-method-argument
        return pq.ops.C(pq.ops.ZGate())

class Toffoli(BasicProjectQGate): # pylint: disable=too-few-public-methods
    """Class for the Toffoli gate.

    Contrary to other gates, ProjectQ does not have a class for the Toffoli gate,
    as it is implemented as a meta-gate.
    For consistency we define this class, whose constructor is made to retun
    a gate with the correct properties by overwriting __new__().
    """
    def __new__(*par): # pylint: disable=no-method-argument
        return pq.ops.C(pq.ops.ZGate(), 2)

class AllZGate(BasicProjectQGate): # pylint: disable=too-few-public-methods
    """Class for the AllZ gate.

    Contrary to other gates, ProjectQ does not have a class for the AllZ gate,
    as it is implemented as a meta-gate.
    For consistency we define this class, whose constructor is made to retun
    a gate with the correct properties by overwriting __new__().
    """
    def __new__(*par): # pylint: disable=no-method-argument
        return pq.ops.Tensor(pq.ops.ZGate())

class Rot(BasicProjectQGate):
    """Class for the arbitrary single qubit rotation gate.

    ProjectQ does not currently have an arbitrary single qubit rotation gate, so we provide a class that return a suitable combination of rotation gates assembled into a single gate from the constructor of this class.
    """
    def __new__(*par):
        operation1 = pq.ops.Rz(par[1])
        operation2 = pq.ops.Ry(par[2])
        operation3 = pq.ops.Rz(par[3])
        rot_gate = BasicProjectQGate(par[0].__name__)
        rot_gate.matrix = np.dot(operation3.matrix, operation2.matrix, operation1.matrix)
        return rot_gate

class QubitUnitary(BasicProjectQGate): # pylint: disable=too-few-public-methods
    """Class for the QubitUnitary gate.

    ProjectQ does not currently have a real arbitrary QubitUnitary gate, but it allows to directly set the matrix of single qubit gates and can then still decompose them into the elementary gates set, so we do this here.
    """
    def __new__(*par):
        unitary_gate = BasicProjectQGate(par[0].__name__)
        unitary_gate.matrix = np.matrix(par[1])
        return unitary_gate
