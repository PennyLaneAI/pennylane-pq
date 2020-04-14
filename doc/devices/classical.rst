The Classical device
====================

This device is based on ProjectQ's
`"classical" simulator backend <https://projectq.readthedocs.io/en/latest/projectq.backends.html#projectq.backends.ClassicalSimulator>`_,
which only allows classical gates such as NOTs.

The device is created in PennyLane as follows:

.. code-block:: python

    import pennylane as qml
    dev = qml.device('projectq.classical', wires=XXX)
