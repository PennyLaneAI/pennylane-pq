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
Expectations
############

.. currentmodule:: openqml_pq.expval

.. todo::
    They way to present the following depends on the whether the `extra_operations` machinery makes it into the final release.

In addition to the suitable default operations native to OpenQML, the devices of the ProjectQ plugin support a number of additional operations that can be used alongside the native OpenQML operations when defining quantum functions:

.. autosummary::
   AllPauliZ
"""

from openqml.operation import Expectation

class AllPauliZ(Expectation):
    r"""Measure Pauli Z on all qubits.

    .. math:: AllPauliZ = \sigma_z \otimes\dots\otimes \sigma_z

    """
    n_params = 0
    n_wires = 0
