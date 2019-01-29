PennyLane ProjectQ Plugin
#########################

.. image:: https://img.shields.io/travis/com/XanaduAI/pennylane-pq/master.svg?style=for-the-badge
    :alt: Travis
    :target: https://travis-ci.com/XanaduAI/pennylane-pq

.. image:: https://img.shields.io/codecov/c/github/xanaduai/pennylane-pq/master.svg?style=for-the-badge
    :alt: Codecov coverage
    :target: https://codecov.io/gh/XanaduAI/pennylane-pq

.. image:: https://img.shields.io/codacy/grade/6ed6d8397b814fbaa754757fed3ea536.svg?style=for-the-badge
    :alt: Codacy grade
    :target: https://app.codacy.com/app/XanaduAI/pennylane-pq?utm_source=github.com&utm_medium=referral&utm_content=XanaduAI/pennylane-pq&utm_campaign=badger

.. image:: https://img.shields.io/readthedocs/pennylane-pq.svg?style=for-the-badge
    :alt: Read the Docs
    :target: https://pennylane-pq.readthedocs.io

.. image:: https://img.shields.io/pypi/v/PennyLane-PQ.svg?style=for-the-badge
    :alt: PyPI
    :target: https://pypi.org/project/PennyLane-PQ

.. image:: https://img.shields.io/pypi/pyversions/PennyLane-PQ.svg?style=for-the-badge
    :alt: PyPI - Python Version
    :target: https://pypi.org/project/PennyLane-PQ

.. header-start-inclusion-marker-do-not-remove

`PennyLane <https://pennylane.readthedocs.io>`_ is a cross-platform Python library for quantum machine
learning, automatic differentiation, and optimization of hybrid quantum-classical computations.

`ProjectQ <https://projectq.readthedocs.io>`_ is an open-source compilation framework capable of targeting various types of hardware and a high-performance quantum computer simulator with emulation capabilities, and various compiler plug-ins.

This PennyLane plugin allows to use both the software and hardware backends of ProjectQ as devices for PennyLane.


Features
========

* Provides three devices to be used with PennyLane: ``projectq.simulator``, ``projectq.ibm``, and ``projectq.classical``. These provide access to the respective ProjectQ backends.

* Supports a wide range of PennyLane operations and expectation values across the devices.

* Combine ProjectQ high performance simulator and hardware backend support with PennyLane's automatic differentiation and optimization.

.. header-end-inclusion-marker-do-not-remove
.. installation-start-inclusion-marker-do-not-remove

Installation
============

This plugin requires Python version 3.5 and above, as well as PennyLane and ProjectQ. Installation of this plugin, as well as all dependencies, can be done using pip:

.. code-block:: bash

    $ python -m pip install pennylane_pq

To test that the PennyLane ProjectQ plugin is working correctly you can run

.. code-block:: bash

    $ make test

in the source folder. Tests restricted to a specific device can be run by executing :code:`make test-simulator`, :code:`make test-ibm`, or :code:`make test-classical`.

.. note:: Tests on the `ibm device <https://pennylane-pq.readthedocs.io/en/latest/devices.html#projectqibmbackend>`_ can only be run if a :code:`user` and :code:`password` for the `IBM Q experience <https://quantumexperience.ng.bluemix.net/qx/experience>`_ are configured in the `PennyLane configuration file <https://pennylane.readthedocs.io/en/latest/code/configuration.html>`_. If this is the case, running :code:`make test` also executes tests on the :code:`ibm` device. By default tests on the :code:`ibm` device run with :code:`hardware=False`. At the time of writing this means that the test are "free". Please verify that this is also the case for your account.

.. installation-end-inclusion-marker-do-not-remove
.. gettingstarted-start-inclusion-marker-do-not-remove

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

In order to avoid accidentally publishing your credential, you should better specify them via the `PennyLane configuration file <https://pennylane.readthedocs.io/en/latest/code/configuration.html>`_ by adding a section such as

.. code::

  [projectq.global]

    [projectq.ibm]
    user = "XXX"
    password = "XXX"

.. gettingstarted-end-inclusion-marker-do-not-remove

Please refer to the `documentation of the PennyLane ProjectQ Plugin <https://pennylane-pq.readthedocs.io/>`_ as well as well as to the `documentation of PennyLane <https://pennylane.readthedocs.io/>`_ for further reference.

.. howtocite-start-inclusion-marker-do-not-remove

How to cite
===========

If you are doing research using PennyLane, please cite `our whitepaper <https://arxiv.org/abs/1811.04968>`_:

  Ville Bergholm, Josh Izaac, Maria Schuld, Christian Gogolin, and Nathan Killoran. PennyLane. *arXiv*, 2018. arXiv:1811.04968

.. howtocite-end-inclusion-marker-do-not-remove

Contributing
============

We welcome contributions - simply fork the repository of this plugin, and then make a
`pull request <https://help.github.com/articles/about-pull-requests/>`_ containing your contribution.  All contributers to this plugin will be listed as authors on the releases.

We also encourage bug reports, suggestions for new features and enhancements, and even links to cool projects or applications built on PennyLane.


Authors
=======

Christian Gogolin, Maria Schuld, Josh Izaac, Nathan Killoran, and Ville Bergholm

.. support-start-inclusion-marker-do-not-remove

Support
=======

- **Source Code:** https://github.com/XanaduAI/pennylane-pq
- **Issue Tracker:** https://github.com/XanaduAI/pennylane-pq/issues

If you are having issues, please let us know by posting the issue on our Github issue tracker.

.. support-end-inclusion-marker-do-not-remove
.. license-start-inclusion-marker-do-not-remove

License
=======

The PennyLane ProjectQ plugin is **free** and **open source**, released under the `Apache License, Version 2.0 <https://www.apache.org/licenses/LICENSE-2.0>`_.

.. license-end-inclusion-marker-do-not-remove
