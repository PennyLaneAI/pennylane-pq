"""Simple qubit optimization example.

In this demo, we perform rotation on one qubit, entangle it
to a second qubit, and then measure the state of the second qubit.
We then optimize the rotation so that the second qubit is measured
in state |1> with certainty.
"""

import openqml as qm
from openqml import numpy as np
from openqml.optimize import GradientDescentOptimizer, AdagradOptimizer

dev = qm.device('projectq.simulator', wires=1)


@qm.qfunc(dev)
def circuit(variables):
    """QNode"""
    qm.RX(variables[0], [0])
    qm.RY(variables[1], [0])
    return qm.expval.PauliZ(0)


def objective(variables):
    """Cost function to be minimized."""
    return circuit(variables)


vars_init = np.array([0.01, 0.01])
print('Initial rotation angles:', vars_init)
print('Initial cost: {: 0.7f}'.format(objective(vars_init)))

print('\nGradient descent Optimizer')
o = GradientDescentOptimizer(0.5)
variables = vars_init
for it in range(100):
    variables = o.step(objective, variables)
    if it % 5 == 0:
        print('Cost after step {:5d}: {: 0.7f}'.format(it + 1, objective(variables)))
print('Optimized rotation angles:', variables)

print('\nAdagrad Optimizer')
o = AdagradOptimizer(0.5)
variables = vars_init
for it in range(100):
    variables = o.step(objective, variables)
    if it % 5 == 0:
        print('Cost after step {:5d}: {: 0.7f}'.format(it + 1, objective(variables)))
print('Optimized rotation angles:', variables)
