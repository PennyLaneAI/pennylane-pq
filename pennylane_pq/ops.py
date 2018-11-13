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

.. currentmodule:: pennylane_pq.ops

In addition to the suitable default operations native to PennyLane,
the devices of the ProjectQ plugin support a number of additional operations
that can be used alongside the native PennyLane operations when defining
quantum functions:

.. autosummary::
   S
   T
   SqrtX
   SqrtSwap
   .. AllPauliZ

.. note::
    For convenience, and to mirror the behavior of the operations built into
    PennyLane, the operations defined here are also accessible directly under
    the top-level :code:`pennylane_pq` context, i.e., you can use
    :code:`pennylane_pq.S([0])` instead of :code:`pennylane_pq.ops.S([0])`
    when defining a :code:`QNode` using the :code:`qnode` decorator.

"""

from pennylane.operation import Operation

class S(Operation): #pylint: disable=invalid-name,too-few-public-methods
    r"""S gate.

    .. math:: S = \begin{bmatrix} 1 & 0 \\ 0 & i \end{bmatrix}

    Args:
        wires (int): the subsystem the gate acts on
    """
    num_params = 0
    num_wires = 1
    par_domain = None


class T(Operation): #pylint: disable=invalid-name,too-few-public-methods
    r"""T gate.

    .. math:: T = \begin{bmatrix}1&0\\0&\exp(i \pi / 4)\end{bmatrix}

    Args:
        wires (int): the subsystem the gate acts on
    """
    num_params = 0
    num_wires = 1
    par_domain = None

class SqrtX(Operation):
    r"""Square root X gate.

    .. math:: SqrtX = \begin{bmatrix}1+i&1-i\\1-i&1+i\end{bmatrix}

    Args:
        wires (int): the subsystem the gate acts on
    """
    num_params = 0
    num_wires = 1
    par_domain = None

class SqrtSwap(Operation): #pylint: disable=too-few-public-methods
    r"""Square root SWAP gate.

    .. math:: SqrtSwap = \begin{bmatrix}1&0&0&0\\0&(1+i)/2&(1-i)/2&0\\
                                        0&(1-i)/2 &(1+i)/2&0\\0&0&0&1\end{bmatrix}

    Args:
        wires (seq[int]): the subsystems the gate acts on
    """
    num_params = 0
    num_wires = 2
    par_domain = None

# class Toffoli(Operation): #pylint: disable=too-few-public-methods
#     r"""Apply the Tofoli gate.
#     """
#     num_params = 0
#     num_wires = 3
#     par_domain = None

# class AllPauliZ(Operation):
#     r"""Apply Pauli Z to all wires.

#     .. math:: AllPauliZ = \sigma_z \otimes\dots\otimes \sigma_z

#     .. todo:: Potentially remove this gate depending on how
#               https://github.com/XanaduAI/pennylane/issues/61 is resolved.

#     """
#     num_params = 0
#     num_wires = 0
#     par_domain = None
