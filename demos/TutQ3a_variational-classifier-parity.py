"""Variational quantum classifier

This example shows that a variational quantum classifier
can be optimized to reproduce the parity function.

"""

import pennylane as qm
from pennylane import numpy as onp
import numpy as np
from pennylane.optimize import AdagradOptimizer

dev = qm.device('projectq.simulator', wires=4)


def layer(W):
    """ Single layer of the quantum neural net."""

    qm.Rot(W[0, 0], W[0, 1], W[0, 2], [0])
    qm.Rot(W[1, 0], W[1, 1], W[1, 2], [1])
    qm.Rot(W[2, 0], W[2, 1], W[2, 2], [2])
    qm.Rot(W[3, 0], W[3, 1], W[3, 2], [3])

    qm.CNOT([0, 1])
    qm.CNOT([1, 2])
    qm.CNOT([2, 3])
    qm.CNOT([3, 0])


def statepreparation(x):
    """ Encodes data input x into quantum state."""

    qm.BasisState(x, wires=[0, 1, 2, 3])


@qm.qnode(dev)
def circuit(weights, x=None):
    """The circuit of the variational classifier."""

    statepreparation(x)

    for W in weights:
        layer(W)

    return qm.expval.PauliZ(0)


def variational_classifier(vars, x=None, shape=None):
    """The variational classifier."""

    weights = onp.reshape(vars[1:], shape)
    outp = circuit(weights, x=x)

    return outp + vars[0]


def square_loss(labels, predictions):
    """ Square loss function

    Args:
        labels (array[float]): 1-d array of labels
        predictions (array[float]): 1-d array of predictions
    Returns:
        float: square loss
    """
    loss = 0
    for l, p in zip(labels, predictions):
        loss += (l-p)**2
    loss = loss/len(labels)

    return loss


def accuracy(labels, predictions):
    """ Share of equal labels and predictions

    Args:
        labels (array[float]): 1-d array of labels
        predictions (array[float]): 1-d array of predictions
    Returns:
        float: accuracy
    """

    loss = 0
    for l, p in zip(labels, predictions):
        if abs(l-p) < 1e-5:
            loss += 1
    loss = loss/len(labels)

    return loss


def cost(weights, features, labels, shape=None):
    """Cost (error) function to be minimized."""

    predictions = [variational_classifier(weights, x=f, shape=shape) for f in features]

    return square_loss(labels, predictions)


# load parity data
data = np.loadtxt("parity.txt")
X = data[:, :-1]
Y = data[:, -1]
Y = Y*2 - np.ones(len(Y))  # shift label from {0, 1} to {-1, 1}

# initialize weight layers
num_qubits = 4
num_layers = 2
vars_init = 0.01 * np.random.randn(num_qubits*3*num_layers+1)
shp = (num_layers, num_qubits, 3)

# create optimizer
o = AdagradOptimizer(0.5)
batch_size = 5

# train the variational classifier
vars = vars_init
for it in range(10):

    # Update the weights by one optimizer step
    batch_index = np.random.randint(0, len(X), (batch_size, ))
    X_batch = X[batch_index]
    Y_batch = Y[batch_index]
    vars = o.step(lambda v: cost(v, X, Y, shape=shp), vars)

    # Compute accuracy
    predictions = [np.sign(variational_classifier(vars, x=x, shape=shp)) for x in X]
    acc = accuracy(Y, predictions)

    print("Iter: {:5d} | Cost: {:0.7f} | Accuracy: {:0.7f} "
          "".format(it+1, cost(vars, X, Y), acc))
