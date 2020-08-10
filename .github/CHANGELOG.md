# Release 0.9.0-dev

### New features since last release

### Breaking changes

### Improvements

### Documentation

* The documentation theme has been updated, and the documentation structure
  reorganized.
  [(#60)](https://github.com/XanaduAI/pennylane-pq/pull/60)

### Bug fixes

* Updated the plugin to use the latest IBMQBackend from ProjectQ.
  [(#62)](https://github.com/XanaduAI/pennylane-pq/pull/61)

### Contributors

This release contains contributions from (in alphabetical order):

Maria Schuld

---

# Release 0.8.0

### Bug fixes

* Adding the 'model': 'qubit' entry into the capabilities dictionary. Adjusting tests that previously used CV operators to use custom created operators.
  ([#56](https://github.com/XanaduAI/pennylane-pq/pull/56))

### Contributors

This release contains contributions from (in alphabetical order):

Antal Szava

---

# Version 0.6.0

### Bug fixes

* The way measurement statistics works has changed in the latest version of PennyLane. Now, rather
  than `shots=0` referring to 'analytic' mode, there is a separate analytic argument.
  Further, the num_shots argument has been removed from Device.samples().
  ([#53](https://github.com/XanaduAI/pennylane-pq/pull/53))

### Contributors

This release contains contributions from (in alphabetical order):

Josh Izaac

---

# Version 0.4.1

### Bug fixes

* Remove opening of `requirements.txt` from within `setup.py`. This avoids a `FileNotFoundError` if installing via `pip`, as Python renames this file during packaging to `requires.txt`.
  ([#53](https://github.com/XanaduAI/pennylane-pq/pull/53))

### Contributors

This release contains contributions from (in alphabetical order):

Josh Izaac

---

# Version 0.4.0

### New features

* Adds support for PennyLane version 0.4. This includes:

  - Renaming expectation -> observable in various places in the documentation
  - Device.expectations -> Device.observables
  - Device.pre_expval -> Device.pre_measure
  - Device.post_expval -> Device.

* Adds support for `pennylane.var()` QNode return type

* Updates the minimum required PennyLane version to 0.4

* Update the documentation to reflect PennyLane v0.4 support

### Contributors

This release contains contributions from (in alphabetical order):

Josh Izaac

---

# Version 0.2.1

### Bug fixes

* Allows PennyLane-ProjectQ devices to be used with all newer version of PennyLane, not just version 0.2.0.

### Contributors

This release contains contributions from (in alphabetical order):

Josh Izaac

---

# Version 0.2

### New features

* Adds support for PennyLane v0.2

* Increases the number of supported measurements on the IBM backend by automatically applying operations before the the final measurement (which is always in the `PauliZ` basis) (#38)

* Adds support for the new PennyLane Identity expectation in all devices provided by this plugin (#36)

* The simulator backend now supports the simulation of finite statistics expectation values if shots!=0, by sampling from the exact probability distribution (#35)

### Improvements

* Improved the documentation of specifying credentials via the configuration file (#48)

* Improves the handling of kwargs and the corresponding documentation (#39)

* Corrected and improved documentation of the supported operations

### Contributors

This release contains contributions from (in alphabetical order):

Christian Gogolin

---

# Version 0.1

First public release of PennyLane ProjectQ plugin.

### Contributors

This release contains contributions from (in alphabetical order):

Christian Gogolin, Maria Schuld, Josh Izaac, Nathan Killoran, and Ville Bergholm.
