Tutorials
=========

To see the PennyLane ProjectQ plugin in action you can use any of the `qubit based tutorials <https://pennylane.readthedocs.io/en/latest/tutorials/notebooks.html>`_ from the documentation of PennyLane and run them on a ``'projectq.simulator'`` device by replacing the ``'default.qubit'`` device used there with

.. code-block:: python

    dev = qml.device('projectq.simulator', wires=XXX)

for an appropriate number of wires.

You can also try to run, e.g., the qubit rotation code on actual quantum hardware by using the ``'projectq.ibm'`` device.
