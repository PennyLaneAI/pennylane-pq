"""Variational quantum classifier.

In this demo we implement a variational classifier inspired by
Schuld et al. 2018 (arXiv:1804.00633).
"""

import openqml as qm
from openqml import numpy as onp
import numpy as np
from openqml.optimize import AdagradOptimizer
import matplotlib.pyplot as plt

from math import isclose

dev = qm.device('default.qubit', wires=2)


def layer(W):
    """ Single layer of the quantum neural net
    with CNOT range 1."""

    qm.Rot(W[0, 0], W[0, 1], W[0, 2], [0])
    qm.Rot(W[1, 0], W[1, 1], W[1, 2], [1])

    qm.CNOT([0, 1])


def get_beta(x):
    """Compute coefficients needed to prepare a quantum state
    whose ket vector is `x`"""

    beta1 = 2*np.arcsin(np.sqrt(x[1]**2) / np.sqrt(x[0]**2 + x[1]**2))
    beta2 = 2*np.arcsin(np.sqrt(x[3]**2) / np.sqrt(x[2]**2 + x[3]**2))
    beta3 = 2*np.arcsin(np.sqrt(x[2]**2 + x[3]**2) / np.sqrt(x[0]**2 + x[1]**2 + x[2]**2 + x[3]**2))

    return beta1/2, beta2/2, beta3


def statepreparation(beta):
    """ """

    qm.RY(beta[0], [1])
    qm.CNOT([0, 1])
    qm.RY(-beta[0], [1])
    qm.CNOT([0, 1])
    qm.RY(beta[1], [1])
    qm.PauliX([0])
    qm.CNOT([0, 1])
    qm.RY(-beta[1], [1])
    qm.CNOT([0, 1])
    qm.PauliX([0])
    qm.RY(beta[2], [0])


@qm.qnode(dev)
def circuit(weights, x=None):
    """The circuit of the variational classifier."""

    #statepreparation(data)

    qm.QubitStateVector(x, [0, 1])

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
        if isclose(l, p, abs_tol=1e-5):
            loss += 1
    loss = loss/len(labels)

    return loss


def regularizer(weights):
    """L2 Regularizer penalty on weights

    Args:
        weights (array[float]): The array of trainable weights
    Returns:
        float: regularization penalty
    """
    w_flat = weights.flatten()

    # Compute the l2 norm
    reg = onp.abs(onp.inner(w_flat, w_flat))

    return reg


def cost(weights, features, labels, shape=None):
    """Cost (error) function to be minimized."""

    predictions = [variational_classifier(weights, x=f, shape=shape) for f in features]

    return square_loss(labels, predictions) #+ regularizer(weights)


# load Iris data and normalise feature vectors
data = np.loadtxt("iris_scaled.txt")
X = data[:, :-1]
normalization = np.sqrt(np.sum(X ** 2, -1))
X = (X.T / normalization).T  # normalize each input
features = X
#features = np.array([get_beta(x) for x in X]) # compute feature vectors

Y = data[:, -1]
labels = Y*2 - np.ones(len(Y))  # shift from {0, 1} to {-1, 1}

# split into training and validation set
num_data = len(labels)
num_train = int(0.75*num_data)
index = np.random.permutation(range(num_data))
feats_train = features[index[: num_train]]
labels_train = labels[index[: num_train]]
feats_val = features[index[num_train: ]]
labels_val = labels[index[num_train: ]]

# initialize weight layers
num_qubits = 2
num_layers = 4
weights0 = 0.01*np.random.randn(num_qubits*3*num_layers+1)
shp = (num_qubits, 3, num_layers)

# create optimizer
o = AdagradOptimizer(0.01)

# train the variational classifier
batch_size = 5
weights = weights0

for iteration in range(15):
    print(weights[0])

    # Update the weights by one optimizer step
    batch_index = np.random.randint(0, num_train, (batch_size, ))
    feats_train_batch = feats_train[batch_index]
    labels_train_batch = labels_train[batch_index]
    weights = o.step(lambda w: cost(w, feats_train_batch, labels_train_batch, shape=shp), weights)

    # Compute predictions on train and validation set
    predictions_train = [np.sign(variational_classifier(weights, x=f, shape=shp)) for f in feats_train]
    predictions_val = [np.sign(variational_classifier(weights, x=f, shape=shp)) for f in feats_val]

    # Compute accuracy on train and validation set
    acc_train = accuracy(labels_train, predictions_train)
    acc_val = accuracy(labels_val, predictions_val)

    print("Iter: {:5d} | Cost: {:0.7f} | Acc train: {:0.7f} | Acc validation: {:0.7f} "
          "".format(iteration, cost(weights, X, Y), acc_train, acc_val))



import matplotlib.pyplot as plt

plt.figure()
cm = plt.cm.RdBu

# make data for decision regions
xx, yy = np.meshgrid(np.linspace(-1.1, 1.1, 20), np.linspace(-1.1, 1.1, 20))
X_grid = [np.array([0, 0, x, y]) for x, y in zip(xx.flatten(), yy.flatten())]
predictions_grid = [variational_classifier(weights, x=x) for x in X_grid]
Z = np.reshape(predictions_grid, xx.shape)

# plot decision regions
cnt = plt.contourf(xx, yy, Z, levels=np.arange(-1, 1.1, 0.1), cmap=cm, alpha=.8, extend='both')
plt.colorbar(cnt, ticks=[-1, 0, 1])

# plot data
trf0 = [d for i, d in enumerate(feats_train) if labels_train[i] == -1]
trf1 = [d for i, d in enumerate(feats_train) if labels_train[i] == 1]
plt.scatter([c[0] for c in trf1], [c[1] for c in trf1], c='r', marker='^', edgecolors='k')
plt.scatter([c[0] for c in trf0], [c[1] for c in trf0], c='r', marker='o', edgecolors='k')
tes0 = [d for i, d in enumerate(feats_val) if labels_val[i] == -1]
tes1 = [d for i, d in enumerate(feats_val) if labels_val[i] == 1]
plt.scatter([c[0] for c in tes1], [c[1] for c in tes1], c='g', marker='^', edgecolors='k')
plt.scatter([c[0] for c in tes0], [c[1] for c in tes0], c='g', marker='o', edgecolors='k')

plt.xlim(-1, 1)
plt.ylim(-1, 1)
plt.show()