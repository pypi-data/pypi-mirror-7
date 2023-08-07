Fluent Unit Testing
===================

*"When a failing test makes us read 20+ lines of test code,
we die inside."* - C.J. Gaconnet

|Version| |Downloads| |Status| |License|

Why?
~~~~

This is an attempt to make Python testing more readable while maintaining a
Pythonic look and feel.  As powerful and useful as the `unittest`_ module is,
I've always disliked the Java-esque naming convention amongst other things.

While truly awesome, attempts to bring BDD to Python never feel *Pythonic*.
Most of the frameworks that I have seen rely on duplicated information between
the specification and the test cases.  My belief is that we need something
closer to what `RSpec`_ offers but one that feels like Python.

Where?
~~~~~~

- Source Code: https://github.com/dave-shawley/fluent-test
- CI: https://travis-ci.org/dave-shawley/fluent-test
- Documentation: https://fluent-test.readthedocs.org/

How?
~~~~

`fluenttest.test_case.TestCase` implements the Arrange, Act, Assert method
of testing.  The configuration for the test case and the execution of the
single action under test is run precisely once per test case instance.
The test case contains multiple assertions each in its own method.  The
implementation leverages existing test case runners such as `nose`_ and
`py.test`_.  In order to run the arrange and act steps once per test,
fluenttest calls ``arrange`` and ``act`` from within the ``setUpClass``
class method.  Each assertion is then written in its own test method.
The following snippet rewrites the simple example from the Python Standard
library unittest documentation::

   import random
   import unittest

   class TestSequenceFunctions(unittest.TestCase):
      def setUp(self):
         self.seq = list(range(10))

      def test_shuffle(self):
         # make sure the shuffled sequence does not lose any elements
         random.shuffle(self.seq)
         self.seq.sort()
         self.assertEqual(self.seq, list(range(10)))

         # should raise an exception for an immutable sequence
         self.assertRaises(TypeError, random.shuffle, (1, 2, 3))

This very simple test looks like the following when written using
``fluenttest``.  Notice that the comments in the original test really
pointed out that there were multiple assertions buried in the test
method.  This is much more explicit with ``fluenttest``::

   import random
   import unittest

   from fluenttest import test_case

   class WhenShufflingSequence(test_case.TestCase, unittest.TestCase):
       @classmethod
       def arrange(cls):
           super(WhenShufflingSequence, cls).arrange()
           cls.input_sequence = list(range(10))
           cls.result_sequence = cls.input_sequence[:]

       @classmethod
       def act(cls):
           random.shuffle(cls.result_sequence)

       def test_should_not_loose_elements(self):
           self.assertEqual(sorted(self.result_sequence),
                            sorted(self.input_sequence))

   class WhenShufflingImmutableSequence(test_case.TestCase, unittest.TestCase):
       allowed_exceptions = TypeError

       @classmethod
       def act(cls):
           random.shuffle((1, 2, 3))

       def test_should_raise_type_error(self):
           self.assertIsInstance(self.exception, TypeError)

The ``fluenttest`` version is almost twice the length of the original so
brevity is not a quality to expect from this style of testing.  The first
thing that you gain is that the comments that explained what each test is
doing is replace with very explicit code.  In this simplistic example, the
gain isn't very notable.  Look at the *tests* directory for a realistic
example of tests written in this style.

Contributing
~~~~~~~~~~~~

Contributions are welcome as long as they follow a few basic rules:

1. They start out life by forking the central repo and creating a new
   branch off of *master*.
2. All tests pass and coverage is at 100% - **make test**
3. All quality checks pass - **make lint**
4. Issue a pull-request through github.

Development Environment
-----------------------

Like many other projects, the development environment is contained in a
virtual environment and controlled by a Makefile.  The inclusion of make is
less than perfect, but it is the easiest way to bootstrap a project on just
about any platform.  Start out by cloning the repository with git and
building a virtual environment to work with::

    $ git clone https://github.com/my-org/fluent-test.git
    $ cd fluent-test
    $ make environment

This will create a Python 3 environment in the *env* directory using *mkvenv*
and install the various prerequisites such as *pip* and *nose*.  You can
activate the environment source ``source env/bin/activate``, launch a Python
interpreter with ``env/bin/python``, and run the test suite with
``env/bin/nosetests``.

The Makefile exports a few other useful targets:

- **make test**: run the tests
- **make lint**: run various static analysis tools
- **make clean**: remove cache files
- **make mostly-clean**: remove built and cached eggs
- **make dist-clean**: remove generated distributions
- **make maintainer-clean**: remove virtual environment
- **make sdist**: create a distribution tarball
- **make docs**: build the HTML documentation

.. _unittest: http://docs.python.org/2/library/unittest.html
.. _RSpec: http://rspec.info/
.. _gitflow: https://github.com/nvie/gitflow
.. _nose: http://nose.readthedocs.org
.. _py.test: http://pytest.org

.. |Version| image:: https://badge.fury.io/py/fluent-test.svg
.. |Downloads| image:: https://pypip.in/d/fluent-test/badge.svg
.. |Status| image:: https://travis-ci.org/dave-shawley/fluent-test.svg
.. |License| image:: https://pypip.in/license/fluent-test/badge.svg
