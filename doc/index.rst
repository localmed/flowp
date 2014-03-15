Flowp 1.1
==========
Flowp is a library which tries to bring the best ideas from Ruby / node.js
world to Python making development more fun. For version 1.1 module
flowp.testing is available which allows to write tests in a RSpec BDD
style with minimum of magic and flowp.files module which brings convenient utils
for files processing.

Installation
------------
::

    $ pip3 install flowp

.. note::

    Only for Python >=3.3


User's guide
-------------
.. toctree::
    :maxdepth: 2


    testing
    files

Changes log
---------------------

1.1 (2014-03-15)
^^^^^^^^^^^^^^^^^
* new module: flowp.files utils module
* flowp.testing: new mechanism independent from unittest module,
  uses only unittest.mock for mocking capabilities
* flowp.testing: support for files testing
* flowp.testing: better support for mocking

1.0 (2013-12-15)
^^^^^^^^^^^^^^^^^
* initial release
* flowp.testing module only
