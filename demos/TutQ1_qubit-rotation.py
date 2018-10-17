"""Simple qubit optimization example using the ProjectQ simulator backend.

This "hello world" example for PennyLane optimizes a beam splitter
to redirect a photon from the first to the second mode.
"""

import openqml as qm
from openqml import numpy as np
from openqml.optimize import GradientDescentOptimizer

dev = qm.device('projectq.simulator', wires=1)


@qm.qnode(dev)
def circuit(vars):
    """QNode"""
    qm.RX(vars[0], [0])
    qm.RY(vars[1], [0])
    return qm.expval.PauliZ(0)


def objective(vars):
    """Cost function to be minimized."""
    return circuit(vars)


vars_init = np.array([0.01, 0.01])

o = GradientDescentOptimizer(0.5)

vars = vars_init
for it in range(100):
    vars = o.step(objective, vars)

    if (it+1) % 5 == 0:
        print('Cost after step {:5d}: {: 0.7f}'
              .format(it+1, objective(vars)))

print('\nOptimized rotation angles: {}'.format(vars))