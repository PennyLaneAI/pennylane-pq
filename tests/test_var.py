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
Unit tests for variance
"""
from unittest.mock import MagicMock
import pytest

import numpy as np
import pennylane
from pennylane.wires import Wires

from defaults import TOLERANCE
from pennylane_pq.devices import ProjectQSimulator, ProjectQClassicalSimulator, ProjectQIBMBackend
import os

token = os.getenv("IBMQX_TOKEN")


@pytest.fixture
def tol():
    """Numerical tolerance"""
    return TOLERANCE


@pytest.fixture
def dev(DevClass, monkeypatch):
    """devices"""
    if issubclass(DevClass, ProjectQSimulator):
        yield DevClass(wires=1, shots=20000000, verbose=True)

    elif issubclass(DevClass, ProjectQClassicalSimulator):
        yield DevClass(wires=1, verbose=True)

    elif issubclass(DevClass, ProjectQIBMBackend):
        ibm_options = pennylane.default_config["projectq.ibm"]
        init_device = DevClass(
            wires=1,
            use_hardware=False,
            num_runs=8 * 1024,
            token=token,
            verbose=True,
        )

        with monkeypatch.context() as m:
            m.setattr(
                "pennylane_pq.devices.ProjectQIBMBackend.obs_queue",
                [pennylane.PauliZ(wires=0)],
            )
            init_device._eng = MagicMock()
            init_device._eng.backend = MagicMock()
            init_device._eng.backend.get_probabilities = MagicMock()
            yield init_device


@pytest.mark.parametrize(
    "DevClass", [ProjectQSimulator, ProjectQClassicalSimulator, ProjectQIBMBackend]
)
def test_var_pauliz(dev, tol):
    """Test that variance of PauliZ is the same as I-<Z>^2"""
    dev.apply("PauliX", wires=Wires([0]), par=[])

    if isinstance(dev, ProjectQIBMBackend):
        dev._eng.backend.get_probabilities.return_value = {"0": 0, "1": 1}

    dev.pre_measure()
    var = dev.var("PauliZ", wires=Wires([0]), par=[])
    mean = dev.expval("PauliZ", wires=Wires([0]), par=[])
    dev.post_measure()

    assert np.allclose(var, 1 - mean ** 2, atol=tol, rtol=0)


@pytest.mark.parametrize("DevClass", [ProjectQSimulator, ProjectQIBMBackend])
def test_var_pauliz_rotated_state(dev, tol):
    """test correct variance for <Z> of a rotated state"""
    phi = 0.543
    theta = 0.6543

    dev.apply("RX", wires=Wires([0]), par=[phi])
    dev.apply("RY", wires=Wires([0]), par=[theta])

    if isinstance(dev, ProjectQIBMBackend):
        dev._eng.backend.get_probabilities.return_value = {
            "0": 0.5 * (1 + np.cos(theta) * np.cos(phi)),
            "1": 0.5 * (1 - np.cos(theta) * np.cos(phi)),
        }

    dev.pre_measure()
    var = dev.var("PauliZ", wires=Wires([0]), par=[])
    dev.post_measure()
    expected = 0.25 * (3 - np.cos(2 * theta) - 2 * np.cos(theta) ** 2 * np.cos(2 * phi))

    assert np.allclose(var, expected, atol=tol, rtol=0)
