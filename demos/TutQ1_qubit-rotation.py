"""Simple qubit optimization example using the ProjectQ simulator backend.

This "hello world" example for PennyLane optimizes a beam splitter
to redirect a photon from the first to the second mode.
"""

import openqml as qm
from openqml import numpy as np
from openqml.optimize import GradientDescentOptimizer

dev = qm.device('projectq.simulator', wires=1)


@qm.qfunc(dev)
def circuit(variables):
    """QNode"""
    qm.RX(variables[0], [0])
    qm.RY(variables[1], [0])
    return qm.expectation.PauliZ(0)


def objective(variables):
    """Cost function to be minimized."""
    return circuit(variables)


vars_init = np.array([0.001, 0.001])
print('Initial rotation angles:', vars_init)
print('Initial cost: {: 0.7f}'.format(objective(vars_init)))

print('\nGradient descent Optimizer')
o = GradientDescentOptimizer(0.5)
variables = vars_init
for it in range(100):
    variables = o.step(objective, variables)
    if it % 5 == 0:
        print('Cost after step {:5d}: {: 0.7f} | Variables: {}'
              .format(it+1, objective(variables), variables))
