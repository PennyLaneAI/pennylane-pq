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
Operations
##########

.. currentmodule:: openqml_pq.ops

In addition to the suitable default operations native to OpenQML, the devices of the ProjectQ plugin support a number of additional operations that can be used alongside the native OpenQML operations when defining quantum functions:

.. autosummary::
   S
   T

"""
from openqml.operation import Operation, Expectation

class S(Operation):
    r"""S gate.

    .. todo::
        Why does the math not work here?

    .. math::
        S() = \begin(bmatrix)1&0\\0&i\end(bmatrix)

    Args:
        wires (int): the subsystem the Operation acts on.
    """
    n_params = 0
    n_wires = 1


class T(Operation):
    r"""T gate.

    .. math::
        T() = \begin(bmatrix)1&0\\0&exp(i \pi / 4)\end(bmatrix)

    Args:
        wires (int): the subsystem the Operation acts on.
    """
    n_params = 0
    n_wires = 1

class SqrtX(Operation):
    r"""Square toot X gate.

    .. math::
        SqrtX() = \begin(bmatrix)1+i&1-i\\1-i&1+i\end(bmatrix)

    Args:
        wires (int): the subsystem the Operation acts on.
    """
    n_params = 0
    n_wires = 1

class SqrtSwap(Operation):
    r"""Square SWAP gate.

    .. math::
        SqrtSwap() = \begin(bmatrix)1&0&0&0\\0&(1+i)/2&(1-i)/2&0\\0&(1-i)/2 &(1+i)/2&0\\0&0&0&1\end(bmatrix)

    Args:
        wires (seq[int]): the subsystems the Operation acts on.
    """
    n_params = 0
    n_wires = 2

class AllZ(Expectation):
    r"""Measure Z on all qubits.

    .. math::
        AllZ() = Z \otimes\dots\otimes Z
    """
    n_params = 0
    n_wires = 0
