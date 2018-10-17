"""Variational quantum eigensolver example.

In this demo we optimize a variational circuit to lower
the energy expectation of a user-defined Hamiltonian.

We express the Hamiltonian as a sum of two Pauli operators.
"""

import openqml as qm
from openqml.optimize import GradientDescentOptimizer
import numpy as np

dev = qm.device('projectq.simulator', wires=2)


def ansatz():
    """ Ansatz of the variational circuit."""

    qm.Hadamard([0])
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


def cost(vars):
    """Cost (error) function to be minimized."""

    expX = circuit_X()
    expY = circuit_Y()

    return vars[0]*expX + vars[1]*expY


# optimizer
o = GradientDescentOptimizer(0.5)

# minimize the cost
vars = np.array([0., 0.])
for it in range(20):
    vars = o.step(cost, vars)

    print('Cost after step {:5d}: {: .7f} | Variables: [{: .5f},{: .5f}]'
          .format(it+1, cost(vars), vars[0], vars[1]))


