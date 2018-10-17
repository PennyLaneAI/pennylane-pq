"""Qubit optimization example.

This "hello world" example for PennyLane optimizes two rotation angles
to flip a qubit from state |0> to state |1>.
"""

import openqml as qm
from openqml import numpy as np
from openqml.optimize import GradientDescentOptimizer

dev = qm.device('default.qubit', wires=1)


@qm.qfunc(dev)
def circuit(variables):
    """QNode"""
    qm.RX(variables[0], [0])
    qm.RY(variables[1], [0])
    return qm.expectation.PauliZ(0)


def objective(variables):
    """Cost (error) function to be minimized."""
    return circuit(variables)


o = GradientDescentOptimizer(0.5)

vars = np.array([0.001, 0.001])
print('Initial rotation angles:'.format(vars))
print('Initial cost: {: 0.7f}'.format(objective(vars)))

for it in range(100):
    vars = o.step(objective, vars)
    if it % 5 == 0:
        print('Cost after step {:5d}: {: 0.7f}'.format(it+1, objective(vars)))

print('Optimized rotation angles:'.format(vars))




"""Qubit optimization unit test for the ProjectQ plugin.

In this demo, we perform rotation on one qubit, entangle it via a CNOT
gate to a second qubit, and then measure the second qubit projected onto PauliZ.
We then optimize the circuit such the resulting expectation value is 1.
"""

import unittest
from unittest_data_provider import data_provider

from defaults import BaseTest
import openqml as qm
from openqml import numpy as np
from openqml.optimize import GradientDescentOptimizer

import openqml_pq



class QubitOptimizationTests(BaseTest):
    """Test a simple one qubit rotation gate optimization.
    """
    num_subsystems = 2
    def setUp(self):
        super().setUp()
        self.dev1 = qm.device('projectq.'+self.args.backend, wires=self.num_subsystems, **vars(self.args))


    def all_optimizers():
        return tuple([(optimizer,) for optimizer in qm.optimize.__all__])

    @data_provider(all_optimizers)
    def test_qubit_optimization(self, optimizer):
        """ """
        if optimizer == 'SGD':
            # SGD requires a dataset
            return

        @qm.qnode(self.dev1)
        def circuit(x, y, z):
            qm.RZ(z, [0])
            qm.RY(y, [0])
            qm.RX(x, [0])
            qm.CNOT([0, 1])
            return qm.expval.PauliZ(1)


        def cost(x):
            """Cost (error) function to be minimized."""
            return np.abs(circuit(*x)-1)

        # initialize x with "random" value
        x0 = np.array([0.2,-0.1,0.5])
        o = GradientDescentOptimizer(cost, x0, optimizer=optimizer)

        # train the circuit
        c = o.train(max_steps=100)


        self.assertAllAlmostEqual(circuit(*o.weights), 1, delta=0.002, msg="Optimizer "+optimizer+" failed to achieve the optimal value.")
        self.assertAllAlmostEqual(o.weights[0], 0, delta=0.002, msg="Optimizer "+optimizer+" failed to find the optimal x angles.")
        self.assertAllAlmostEqual(o.weights[1], 0, delta=0.002, msg="Optimizer "+optimizer+" failed to find the optimal y angles.")


if __name__ == '__main__':
    # run the tests in this file
    suite = unittest.TestSuite()
    for t in (QubitOptimizationTests, ):
        ttt = unittest.TestLoader().loadTestsFromTestCase(t)
        suite.addTests(ttt)
    unittest.TextTestRunner().run(suite)
