===============
subunit-details
===============

  **Python Test Detail attachment extractor for SubUnit streams.**

----

 * Requires:
    - Python 3.x
    - subunit
    - testtools

 * Author:
    - Corey Goldberg, 2014

----

About SubUnit:
--------------

  `SubUnit <https://launchpad.net/subunit>`_ is a streaming protocol for test results. The protocol is a binary encoding that is easily generated and parsed. By design all the components of the protocol conceptually fit into the ``xUnit`` ``TestCase -> TestResult`` interaction.

Test Details:
-------------------

  `Details <http://testtools.readthedocs.org/en/latest/for-test-authors.html#details>`_ may be attached from a ``TestCase``, using the `testtools <http://testtools.readthedocs.org/>`_ library (extension to Python's standard ``unittest`` lib).  They will end up as attachments to the ``TestResult``.  Using ``subunit``, the detail attachments may be of any format and mime-type, and can be parsed and retrieved.

About subunit-details:
----------------------

  Given a binary subunit stream stored as a file, the ``subunitdetails`` script will extract test detail attachments and save them individually to the filesystem.

Using subunit-details to extract attachments:
----------------------------------------------------

 * Invoke the ``subunitdetails`` script, with a subunit file name as an argument::

    $ subunitdetails <subunit_file>

Installing:
-----------

 `subunit-details <http://pypi.python.org/pypi/subunit-details>`_ uses standard python packaging via `setuptools <https://pypi.python.org/pypi/setuptools>`_.

 There are a few options to choose from for installing:


 * install from PyPI, system-wide::

    $ sudo pip install subunit-details

 * install from PyPI, using a virtualenv::

    $ virtualenv -p python3 .env
    $ source .env/bin/activate
    $ pip install subunit-details

 * clone the dev repository and install, system-wide::

    $ git clone https://github.com/cgoldberg/subunit-details.git
    $ cd subunit-details
    $ sudo python3 setup install

 * clone the dev repository and install, using a virtualenv::

    $ git clone https://github.com/cgoldberg/subunit-details.git
    $ cd subunit-details
    $ virtualenv -p python3 .env
    $ source .env/bin/activate
    $ python3 setup install
