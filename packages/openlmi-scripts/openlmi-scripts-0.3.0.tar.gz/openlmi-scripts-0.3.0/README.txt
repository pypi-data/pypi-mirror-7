openlmi-scripts
===============

Client-side python libraries and *LMI Meta-command* for system
management through OpenLMI providers.

It serves as a base for small python eggs targeted on one or more
OpenLMI providers. We call these eggs scripts. They are installed
separately although they can depend on each other.

They contain python library itself as well as command line interface.
This interface is registered with *LMI Meta-command* which is a part of
OpenLMI Tools. *LMI Meta-command* loads it and offers to interface with
broker through command line.

For more information please refer to online documentation on
`pythonhosted <http://pythonhosted.org/openlmi-tools/index.html>`__.

Take a look at `scripts upstream
repository <https://github.com/openlmi/openlmi-scripts>`__ for
inspiration on how to write your own scripts.

Deprecation warning
~~~~~~~~~~~~~~~~~~~

``openlmi-scripts`` is deprecated egg. It contains just *LMI
Meta-command* which has been moved to ``openlmi-tools`` (version
``0.9.1``). Newer scripts (``openlmi-scripts-*``) now depend just on
``openlmi-tools``. Use this package only with older *tools*.

Dependencies
------------

Code base is written for ``python 2.7``. There are following python
dependencies:

-  openlmi-tools >= 0.9 and < 0.9.1
   (`PyPI <https://pypi.python.org/pypi/openlmi-tools>`__)
-  python-docopt
-  pandoc

Installation
------------

Use standard ``setuptools`` script for installation:

::

    $ cd openlmi-scripts/commands/$CMD
    $ make setup
    $ python setup.py install --user

This installs particular client library and command line interface for
*LMI Meta-command*.

Script eggs are also available on *PyPI*, install them with:

::

    $ # add any provider you want to interact with
    $ pip install --user openlmi-scripts-service openlmi-scripts-software

Check out
`this <https://pypi.python.org/pypi?%3Aaction=search&term=openlmi-scripts&submit=search>`__
site listing all available script eggs.

--------------

