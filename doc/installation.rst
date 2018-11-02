Installation
============

This plugin requires Python version 3.5 and above, as well as PennyLane and ProjectQ. Installation of this plugin, as well as all dependencies, can be done using pip:

.. code-block:: bash

    $ python -m pip install pennylane_pq

To test that the PennyLane ProjectQ plugin is working correctly you can run

.. code-block:: bash

    $ make test

in the source folder. Tests restricted to a specific device can be run by executing :code:`make test-simulator`, :code:`make test-ibm`, or :code:`make test-classical`.

.. note:: Tests on the :class:`ibm <pennylane_pq.devices.ProjectQIBMBackend>` device can only be run if a :code:`user` and :code:`password` for the IBM quantum experience are configured in the `PennyLane configuration file <https://pennylane.readthedocs.io/configuration.html>`_. If this is the case, running :code:`make test` also executes tests on the :code:`ibm` device. By default tests on the :code:`ibm` device run with :code:`hardware=False`. At the time of writing this means that the test are "free". Please verify that this is also the case for your account.
