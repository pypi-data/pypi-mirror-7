Change Log
==========

Version 3.0.0
-------------
- Remove class based testing module.

  After using this library for a while, it has become apparent that the
  class-based testing isn't useful.  It also is rather un-pythonic to
  assert structural type information.  If you are using this, then feel
  free to copy and paste the code from the previous version.

- Remove top-level exports from package __init__.py.

  If you were referencing the test case as ``fluenttest.TestCase``, I
  apologize.  Removing the top level ``import`` statements makes it
  possible to reach into the version information without loading the
  package and its dependencies.

- Switch to Python ``unittest`` naming conventions.

  Using ``setup_class`` and ``teardown_class`` causes problems if you
  run tests with ``unittest.main``.  Not to mention that the Standard
  Library uses ``setUpClass`` and ``tearDownClass`` regardless of how
  un-pythonic the names are.

Version 2.0.1 (15-Feb-2014)
---------------------------
- Correct a packaging version defect.

  *Setup.py* cannot safely retrieve the version from the ``__version__``
  attribute of the package since the import requires ``mock`` to be
  present.  The immediate hot-fix is to duplicate the version number
  until I can come up with a cleaner solution.

Version 2.0.0 (15-Feb-2014)
---------------------------
- Remove ``fluenttest.TestCase.patches`` attribute.

  The ``patches`` attribute was just a little too magical for my tastes and
  it wasn't really necessary.  Removing this attribute also removed the
  ``patch_name`` parameter to :class:`~fluenttest.TestCase.patch`.  The latter
  change actually simplifies things quite a bit since we no longer have to
  derive safe attribute names.

- Add :meth:`fluenttest.TestCase.destroy`
- Switch to semantic versioning
- Expose library version with ``__version__`` attribute
- Add Makefile to simplify development process
- Remove usage of tox

Version 1 (27-Jul-2013)
-----------------------
- Implements :class:`fluenttest.TestCase`
- Implements :class:`fluenttest.ClassTester`
