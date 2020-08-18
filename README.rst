PennyLane ProjectQ Plugin
#########################

.. image:: https://img.shields.io/github/workflow/status/PennyLaneAI/pennylane-pq/Tests/master?logo=github&style=flat-square
    :alt: GitHub Workflow Status (branch)
    :target: https://github.com/PennyLaneAI/pennylane-pq/actions?query=workflow%3ATests

.. image:: https://img.shields.io/codecov/c/github/PennyLaneAI/pennylane-pq/master.svg?logo=codecov&style=flat-square
    :alt: Codecov coverage
    :target: https://codecov.io/gh/PennyLaneAI/pennylane-pq

.. image:: https://img.shields.io/codefactor/grade/github/PennyLaneAI/pennylane-pq/master?logo=codefactor&style=flat-square
    :alt: CodeFactor Grade
    :target: https://www.codefactor.io/repository/github/pennylaneai/pennylane-pq

.. image:: https://img.shields.io/readthedocs/pennylane-pq.svg?logo=read-the-docs&style=flat-square
    :alt: Read the Docs
    :target: https://pennylane-pq.readthedocs.io

.. image:: https://img.shields.io/pypi/v/PennyLane-pq.svg?style=flat-square
    :alt: PyPI
    :target: https://pypi.org/project/PennyLane-pq

.. image:: https://img.shields.io/pypi/pyversions/PennyLane-pq.svg?style=flat-square
    :alt: PyPI - Python Version
    :target: https://pypi.org/project/PennyLane-pq

.. header-start-inclusion-marker-do-not-remove

The PennyLane-ProjectQ plugin integrates the ProjectQ quantum computing library with PennyLane's
quantum machine learning capabilities.

`PennyLane <https://pennylane.readthedocs.io>`_ is a cross-platform Python library for quantum machine
learning, automatic differentiation, and optimization of hybrid quantum-classical computations.

`ProjectQ <https://projectq.readthedocs.io>`_ is an open-source compilation framework capable of
targeting various types of hardware and a high-performance quantum computer simulator with
emulation capabilities, and various compiler plug-ins.

This PennyLane plugin allows to use both the software and hardware backends of ProjectQ as devices for PennyLane.

.. header-end-inclusion-marker-do-not-remove

The documentation can be found at https://pennylane-pq.readthedocs.io.


Features
========

* Provides three devices to be used with PennyLane: ``projectq.simulator``, ``projectq.ibm``, and ``projectq.classical``. These provide access to the respective ProjectQ backends.

* Supports a wide range of PennyLane operations and observables across the devices.

* Combine ProjectQ high performance simulator and hardware backend support with PennyLane's automatic differentiation and optimization.

.. installation-start-inclusion-marker-do-not-remove

Installation
============

This plugin requires Python version 3.5 and above, as well as PennyLane and ProjectQ. Installation of this plugin, as well as all dependencies, can be done using pip:

.. code-block:: bash

    $ python -m pip install pennylane_pq

To test that the PennyLane ProjectQ plugin is working correctly you can run

.. code-block:: bash

    $ make test

in the source folder. Tests restricted to a specific device can be run by executing
:code:`make test-simulator`, :code:`make test-ibm`, or :code:`make test-classical`.

.. note::

    Tests on the `ibm device <https://pennylane-pq.readthedocs.io/en/latest/devices.html#projectqibmbackend>`_
    can only be run if a :code:`user` and :code:`password` for the
    `IBM Q experience <https://quantumexperience.ng.bluemix.net/qx/experience>`_ are configured
    in the `PennyLane configuration file <https://pennylane.readthedocs.io/en/latest/code/api/pennylane.Configuration.html>`_.
    If this is the case, running :code:`make test` also executes tests on the :code:`ibm` device.
    By default tests on the :code:`ibm` device run with :code:`hardware=False`. At the time of writing this
    means that the test are "free". Please verify that this is also the case for your account.

.. installation-end-inclusion-marker-do-not-remove

Please refer to the `documentation of the PennyLane ProjectQ Plugin <https://pennylane-pq.readthedocs.io/>`_
as well as well as to the `documentation of PennyLane <https://pennylane.readthedocs.io/>`_ for further reference.

.. howtocite-start-inclusion-marker-do-not-remove

How to cite
===========

If you are doing research using PennyLane, please cite `our whitepaper <https://arxiv.org/abs/1811.04968>`_:

  Ville Bergholm, Josh Izaac, Maria Schuld, Christian Gogolin, and Nathan Killoran. PennyLane. *arXiv*, 2018. arXiv:1811.04968

.. howtocite-end-inclusion-marker-do-not-remove

Contributing
============

We welcome contributions - simply fork the repository of this plugin, and then make a
`pull request <https://help.github.com/articles/about-pull-requests/>`_ containing your contribution.
All contributers to this plugin will be listed as authors on the releases.

We also encourage bug reports, suggestions for new features and enhancements, and even
links to cool projects or applications built on PennyLane.


Authors
=======

Christian Gogolin, Maria Schuld, Josh Izaac, Nathan Killoran, and Ville Bergholm

.. support-start-inclusion-marker-do-not-remove

Support
=======

- **Source Code:** https://github.com/PennyLaneAI/pennylane-pq
- **Issue Tracker:** https://github.com/PennyLaneAI/pennylane-pq/issues
- **PennyLane Forum:** https://discuss.pennylane.ai

If you are having issues, please let us know by posting the issue on our Github issue tracker, or
by asking a question in the forum.

.. support-end-inclusion-marker-do-not-remove
.. license-start-inclusion-marker-do-not-remove

License
=======

The PennyLane ProjectQ plugin is **free** and **open source**, released under
the `Apache License, Version 2.0 <https://www.apache.org/licenses/LICENSE-2.0>`_.

.. license-end-inclusion-marker-do-not-remove
