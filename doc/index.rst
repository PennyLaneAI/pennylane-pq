OpenQML
#######

:Release: |release|
:Date: |today|

OpenQML is a Python quantum machine learning library by Xanadu Inc. This plugin allows to use both the software and hardware backends of ProjectQ as devices for quantum machine learning with OpenQML.

The following ProjecQ backends are supported by this plugin:

- projectq.backends.Simulator:	Simulator is a compiler engine which simulates a quantum computer using C++-based kernels.
- projectq.backends.ClassicalSimulator	        A simple simulator that only permits classical operations.
- projectq.backends.IBMBackend	The IBM Backend class, which stores the circuit, transforms it to JSON QASM, and sends the circuit through the IBM API.


Getting started
===============

You can instantiate a 'projectq.simulator' device with:

.. code-block:: python

    import openqml as qm
    dev = qm.device('projectq.simulator', wires=2)

This device can then be used just like other devices for the definition and evaluation of QNodes within OpenQML. As simple quantum function that returns the expectation value of a measurement and depends on three classical input parameters would:

.. code-block:: python

    @qm.qfunc(dev)
    def circuit(x, y, z):
        qm.RZ(z, wires=[0])
        qm.RY(y, wires=[0])
        qm.RX(x, wires=[0])
        qm.CNOT(wires=[0, 1])
        return qm.expectation.PauliZ(wires=1)

Running your quantum machine learning code on an IBM Quantum Experience simulator or even a real hardware chip is just as easy. Instead of the device above, you would instantiate a 'projectq.ibm' device by giving your IBM Quantum Experience username and password:

.. code-block:: python

    import openqml as qm
    dev = qm.device('projectq.ibm', wires=2, user="XXX", password="XXX")



How to cite
===========

If you are doing research using OpenQML, please cite #todo: adjust citation

Support
=======

- **Source Code:** https://github.com/XanaduAI/openQML
- **Issue Tracker:** https://github.com/XanaduAI/openQML/issues

If you are having issues, please let us know by posting the issue on our Github issue tracker.

For more details on contributing or performing research with OpenQML, please see
:ref:`research`.

License
=======

OpenQML is **free** and **open source**, released under the Apache License, Version 2.0.


.. toctree::
   :maxdepth: 1
   :caption: Getting started
   :hidden:

   installing
   research

.. toctree::
   :titlesonly:
   :caption: Key concepts
   :hidden:

   introduction
   qfuncs
   autograd_quantum
   quantum_nodes
   hybrid_computation
   conventions
   references


.. toctree::
   :maxdepth: 1
   :caption: API
   :hidden:

   core
   circuit


.. toctree::
   :maxdepth: 1
   :caption: Plugins
   :hidden:

   plugins
   plugins/included_plugins


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
