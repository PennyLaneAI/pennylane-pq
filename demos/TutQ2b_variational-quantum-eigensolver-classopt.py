"""Variational quantum eigensolver example.

In this demo we optimize a variational circuit to lower
the energy expectation of a user-defined Hamiltonian.

We express the Hamiltonian as a sum of two Pauli operators.
"""

import pennylane as qml
from pennylane.optimize import GradientDescentOptimizer
import numpy as np

dev = qml.device('projectq.simulator', wires=2)


def ansatz():
    """ Ansatz of the variational circuit."""

    qml.Rot(0.3, 1.8, 5.4, [1])
    qml.RX(0.5, [0])
    qml.RY(0.9, [1])
    qml.CNOT([0, 1])


@qml.qnode(dev)
def circuit_X():
    """Circuit measuring the X operator for the second qubit"""
    ansatz()
    return qml.expval.PauliX(1)


@qml.qnode(dev)
def circuit_Y():
    """Circuit measuring the Y operator for the second qubit"""
    ansatz()
    return qml.expval.PauliY(1)


def cost(vars):
    """Cost (error) function to be minimized."""

    expX = circuit_X()
    expY = circuit_Y()

    return (vars[0]*expX + vars[1]*expY)**2


# optimizer
o = GradientDescentOptimizer(0.5)

# minimize the cost
vars = np.array([0.3, 2.5])
for it in range(20):
    vars = o.step(cost, vars)

    print('Cost after step {:5d}: {: .7f} | Variables: [{: .5f},{: .5f}]'
          .format(it+1, cost(vars), vars[0], vars[1]))
