"""Variational quantum eigensolver example.

In this demo we optimize a variational circuit to lower
the energy expectation of a user-defined Hamiltonian.

We express the Hamiltonian as a sum of two Pauli operators.
"""

import openqml as qm
from openqml import numpy as np
from openqml.optimize import GradientDescentOptimizer

dev = qm.device('projectq.simulator', wires=2)


def ansatz():
    """ Ansatz of the variational circuit."""

    # Prepare initial state
    qm.Hadamard([0])

    # Execute some parametrized quantum gates
    qm.RX(0.5, [0])
    qm.RY(0.9, [1])
    qm.CNOT([0, 1])


@qm.qnode(dev)
def circuit_X():
    """Circuit measuring the X operator for the second qubit"""
    ansatz()
    return qm.expval.PauliX(1)


@qm.qnode(dev)
def circuit_Y():
    """Circuit measuring the Y operator for the second qubit"""
    ansatz()
    return qm.expval.PauliY(1)


def cost(weights):
    """Cost (error) function to be minimized."""

    expX = circuit_X()
    expY = circuit_Y()

    return weights[0]*expX + weights[1]*expY


print("initializing weights")
weights0 = np.array([0., 0.])
print('Initial weights:', weights0)

print("optimizing the cost")
o = GradientDescentOptimizer(0.5)
weights = weights0
for iteration in np.arange(1, 201):
    weights = o.step(cost, weights)
    print('Cost after step {:5d}: {: .7}'.format(iteration, cost(weights)))
print('Optimized weights:', weights)
