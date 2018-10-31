PennyLane ProjectQ Plugin
#######################

PennyLane is a Python quantum machine learning library by Xanadu Inc. This plugin opens up both the software and hardware backends of ProjectQ to be used as devices for quantum machine learning with PennyLane.


Installation
============

.. [//]: # (.. include:: doc/installation.rst)

This plugin requires Python version 3.5 and above, as well as PennyLane and ProjectQ. Installation of this plugin, as well as all dependencies, can be done using pip:

.. code-block:: bash

    $ python -m pip install pennylane_pq

To test that the PennyLane ProjectQ plugin is working correctly you can run

.. code-block:: bash

    $ make test

in the source folder.


Getting started
===============

You can instantiate a :code:`'projectq.simulator'` device for PennyLane with:

.. code-block:: python

    import pennylane as qml
    dev = qml.device('projectq.simulator', wires=2)

This device can then be used just like other devices for the definition and evaluation of QNodes within PennyLane. A simple quantum function that returns the expectation value of a measurement and depends on three classical input parameters would look like:

.. code-block:: python

    @qml.qnode(dev)
    def circuit(x, y, z):
        qml.RZ(z, wires=[0])
        qml.RY(y, wires=[0])
        qml.RX(x, wires=[0])
        qml.CNOT(wires=[0, 1])
        return qml.expval.PauliZ(wires=1)

You can then execute the circuit like any other function to get the quantum mechanical expectation value.

.. code-block:: python

	circuit(0.2, 0.1, 0.3)

Running your code on an IBM Quantum Experience simulator or even a real hardware chip is just as easy. Instead of the device above, you would instantiate a :code:`'projectq.ibm'` device by giving your IBM Quantum Experience username and password:

.. code-block:: python

    import pennylane as qml
    dev = qml.device('projectq.ibm', wires=2, user="XXX", password="XXX")


How to cite
===========

.. [//]: # (.. include:: doc/howtocite.rst)

.. todo:: change reference and link

If you are doing research using PennyLane, please cite `our whitepaper <https://arxiv.org/abs/XXXX.XXXXX>`_:

  Authors. PennyLane. *arXiv*, 2018. arXiv:XXXX.XXXXX


Contributing
============

We welcome contributions - simply fork the repository of this plugin, and then make a
`pull request <https://help.github.com/articles/about-pull-requests/>`_ containing your contribution.  All contributers to this plugin will be listed as authors on the releases.

We also encourage bug reports, suggestions for new features and enhancements, and even links to cool projects or applications built on PennyLane.


Authors
=======

.. todo:: confirm author list

Christian Gogolin, Ville Bergholm, Maria Schuld, and Nathan Killoran.


Support
=======

.. [//]: # (.. include:: doc/support.rst)

- **Source Code:** https://github.com/XanaduAI/pennylane-pq
- **Issue Tracker:** https://github.com/XanaduAI/pennylane-pq/issues

If you are having issues, please let us know by posting the issue on our Github issue tracker.

.. todo:: adjust this link


License
=======

.. [//]: # (.. include:: doc/license.rst)

The PennyLane ProjectQ plugin is **free** and **open source**, released under the `Apache License, Version 2.0 <https://www.apache.org/licenses/LICENSE-2.0>`_.
