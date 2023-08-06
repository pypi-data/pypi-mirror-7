===============
subunitdetails
===============

Requires:
  - Python 3.x
  - python-subunit
  - testtools

Author:
  - Corey Goldberg, 2014

++++

About subunitdetails:
----------------------

``subunitdetails`` takes a binary encoded ``subunit`` stream, and extracts test details (content object attachments) and saves them to the filesystem.

Using subunitdetails to extract content object attachments:
-----------------------------------------------------------

Invoke the ``subunitdetails`` script, with a ``subunit`` file name as an argument.  It will extract the embedded content objects (test details) from the ``subunit`` result, into the current directory::

    $ subunitdetails <file_name>

++++

About SubUnit:
--------------

`SubUnit <https://launchpad.net/subunit>`_ is a streaming protocol for test results. The protocol is a binary encoding that is easily generated and parsed. By design all the components of the protocol conceptually fit into the ``xUnit`` ``TestCase -> TestResult`` interaction.


About Test Details:
-------------------

`Details <http://testtools.readthedocs.org/en/latest/for-test-authors.html#details>`_ are MIME-based `content objects <http://testtools.readthedocs.org/en/latest/for-test-authors.html#content>`_ that may be attached to a ``TestCase``.  This is done using the `testtools <http://testtools.readthedocs.org/>`_ library (extensions to Python's standard ``unittest`` lib).  It allows you to attach any information that you could possibly conceive of to a test, and allows ``testtools`` to use or serialize that information.

Using ``subunit``, the encoded stream can be parsed.  Test suite results and attached Details (with MIME-types) can then be retrieved.


Installing subunitdetails:
------------------------------

`subunit-details <http://pypi.python.org/pypi/subunit-details>`_ uses standard python packaging via `setuptools <https://pypi.python.org/pypi/setuptools>`_.

There are a few ways to install ``subunitdetails``.

* Install from `PyPI <https://pypi.python.org/pypi/subunitdetails>`_ using `pip <http://pip.readthedocs.org/>`_ (system-wide)::

    $ sudo pip install subunitdetails

* Install from `PyPI <https://pypi.python.org/pypi/subunitdetails>`_ using `pip <http://pip.readthedocs.org/>`_, into a `virtualenv <http://virtualenv.readthedocs.org/>`_:::

    $ virtualenv -p python3 .env
    $ source .env/bin/activate
    $ pip install subunitdetails

* Clone the dev repository and install, using a virtualenv::

    $ git clone https://github.com/cgoldberg/subunitdetails.git
    $ cd subunitdetails
    $ virtualenv -p python3 .env
    $ source .env/bin/activate
    $ python3 setup install
