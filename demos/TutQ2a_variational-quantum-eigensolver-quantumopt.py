"""Variational quantum eigensolver example.

In this example we optimize a variational circuit to lower
the energy expectation of a user-defined Hamiltonian.

We express the Hamiltonian as a sum of two Pauli operators.
"""

import pennylane as qml
from pennylane.optimize import GradientDescentOptimizer
import numpy as np

dev = qml.device('projectq.simulator', wires=2)


def ansatz(weights):
    """ Ansatz of the variational circuit."""

    qml.Rot(0.3, 1.8, 5.4, [1])
    qml.RX(weights[0], [0])
    qml.RY(weights[1], [1])
    qml.CNOT([0, 1])


@qml.qnode(dev)
def circuit_X(vars):
    """Circuit measuring the X operator for the second qubit"""
    ansatz(vars)
    return qml.expval.PauliX(1)


@qml.qnode(dev)
def circuit_Y(vars):
    """Circuit measuring the Y operator for the second qubit"""
    ansatz(vars)
    return qml.expval.PauliY(1)


def cost(vars):
    """Cost (error) function to be minimized."""

    expX = circuit_X(vars)
    expY = circuit_Y(vars)

    return (0.1*expX + 0.5*expY)**2


# optimizer
o = GradientDescentOptimizer(0.5)

# minimize cost
vars = np.array([0.3, 2.5])
for it in range(60):
    vars = o.step(cost, vars)

    print('Cost after step {:5d}: {: .7f} | Variables: [{: .5f},{: .5f}]'
          .format(it+1, cost(vars), vars[0], vars[1]))
