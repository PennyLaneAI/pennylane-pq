OpenQML ProjectQ Plugin
#######

OpenQML is a Python quantum machine learning library by Xanadu Inc. This plugin allows to use both the software and hardware backends of ProjectQ as devices for quantum machine learning with OpenQML.


Features
========
The following ProjecQ backends are supported by this plugin:

- **projectq.backends.Simulator**:		A classical simulator of a quantum computer based on C++ kernels.
- **projectq.backends.ClassicalSimulator**:	A simple classical simulator that only permits classical operations.
- **projectq.backends.IBMBackend**:		The IBM Backend, which allows to run quantum computations on simulators and real quantum hardware via the IBM Q API.


Installation
============

This plugin requires Python version 3.5 and above, as well as OpenQML and ProjectQ. Installation of this plugin, as well as all dependencies, can be done using pip:

.. code-block:: bash

    $ python -m pip install openqml_pq


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

.. include:: doc/howtocite.rst

Contributing
============

We welcome contributions - simply fork the repository of this plugin, and then make a
`pull request <https://help.github.com/articles/about-pull-requests/>`_ containing your contribution.  All contributers to this plugin will be listed as authors on the releases.

We also encourage bug reports, suggestions for new features and enhancements, and even links to cool projects or applications built on OpenQML.


Authors
=======

Christian Gogolin, Ville Bergholm, Maria Schuld, and Nathan Killoran.


Support
=======

- **Source Code:** https://github.com/XanaduAI/openqml-pq
- **Issue Tracker:** https://github.com/XanaduAI/openqml-pq/issues

If you are having issues, please let us know by posting the issue on our Github issue tracker.

.. todo:: adjust this link

We also have an `OpenQML Slack channel <https://u.openqml.ai/slack>`_ -
come join the discussion and chat with our OpenQML team.


License
=======

The OpenQML ProjectQ plugin is **free** and **open source**, released under the `Apache License, Version 2.0 <https://www.apache.org/licenses/LICENSE-2.0>`_.
