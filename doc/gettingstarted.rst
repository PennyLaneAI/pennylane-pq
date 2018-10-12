You can instantiate a `projectq.smulator` device with:

.. code-block:: python

    import openqml as qm
    dev = qm.device('projectq.simulator', wires=2)

This device can then be used just like other devices for the definition and evaluation of `QNodes` within OpenQML. A simple quantum function that returns the expectation value of a measurement and depends on three classical input parameters can be defined like this:

.. code-block:: python

    @qm.qfunc(dev)
    def circuit(x, y, z):
        qm.RZ(z, wires=[0])
        qm.RY(y, wires=[0])
        qm.RX(x, wires=[0])
        qm.CNOT(wires=[0, 1])
        return qm.expectation.PauliZ(wires=1)

Running your quantum machine learning code on an IBM Q simulator or even a real hardware chip is just as easy. Instead of the device above, you would instantiate a `projectq.ibm` device by giving your IBM Quantum Experience username and password:

.. code-block:: python

    import openqml as qm
    dev = qm.device('projectq.ibm', wires=2, user="XXX", password="XXX")
