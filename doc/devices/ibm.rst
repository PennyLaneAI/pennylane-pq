The IBM device
==============

This device uses ProjectQ's interfaces with the
`IBM Quantum Experience backend <https://projectq.readthedocs.io/en/latest/projectq.backends.html#projectq.backends.IBMBackend>`_,
which includes a simulator and access to the hardware.

For this you need to instantiate a :code:`'projectq.ibm'`
device by giving your IBM Quantum Experience username and password:

.. code-block:: python

    import pennylane as qml
    dev = qml.device('projectq.ibm', wires=2, user="XXX", password="XXX")

Storing your credentials
~~~~~~~~~~~~~~~~~~~~~~~~

In order to avoid accidentally publishing your credentials, you should specify them
via the `PennyLane configuration file <https://pennylane.readthedocs.io/en/latest/code/configuration.html>`_
by adding a section such as

.. code::

  [projectq.global]

    [projectq.ibm]
    user = "XXX"
    password = "XXX"
