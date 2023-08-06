Changelog
---------

Here you can see the full list of changes between each pytest-instafail release.

0.3.0 (August 30, 2014)
^^^^^^^^^^^^^^^^^^^^^^^

- Added support for Python 3.4
- Added support for py.test 2.6
- Fixed failing tests on py.test 2.6

0.2.0 (March 6, 2014)
^^^^^^^^^^^^^^^^^^^^^

- Dropped support for Python 2.5.
- Fixed stacktrace printed twice when using PDB.
- Fixed internal error when a test marked as xfailing unexpectedly passes
  (David Szotten).

0.1.1 (November 9, 2013)
^^^^^^^^^^^^^^^^^^^^^^^^

- Made pytest-instafail compatible with `pytest-xdist`_'s test parallelization
  (Ronny Pfannschmidt).

0.1.0 (April 8, 2013)
^^^^^^^^^^^^^^^^^^^^^

- Initial public release

.. _`pytest-xdist`: http://pypi.python.org/pypi/pytest-xdist
