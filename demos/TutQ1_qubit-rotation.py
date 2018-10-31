"""Simple qubit optimization example using the ProjectQ simulator backend.

This "hello world" example for PennyLane optimizes a beam splitter
to redirect a photon from the first to the second mode.
"""

import pennylane as qml
from pennylane import numpy as np
from pennylane.optimize import GradientDescentOptimizer

dev = qml.device('projectq.simulator', wires=1)


@qml.qnode(dev)
def circuit(vars):
    """QNode"""
    qml.RX(vars[0], [0])
    qml.RY(vars[1], [0])
    return qml.expval.PauliZ(0)


def objective(vars):
    """Cost function to be minimized."""
    return circuit(vars)


vars_init = np.array([0.011, 0.012])

o = GradientDescentOptimizer(0.5)

vars = vars_init
for it in range(100):
    vars = o.step(objective, vars)

    if (it+1) % 5 == 0:
        print('Cost after step {:5d}: {: 0.7f}'
              .format(it+1, objective(vars)))

print('\nOptimized rotation angles: {}'.format(vars))
