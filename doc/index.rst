Flowp 1.1
==========
Flowp is a library which tries to bring the best ideas from Ruby / node.js
world to Python making development more fun. For version 1.0 module
flowp.testing is available which allows to write tests in a RSpec BDD
style with minimum of magic.

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
    task

Changes log
---------------------

1.1
^^^^^^^
* new modules: flowp.files and flowp.task
* flowp.testing: new mechanism independent from unittest module,
  uses only unittest.mock for mocking capabilities
* flowp.testing: support for files testing

1.0 (2013-12-15)
^^^^^^^
* initial release
* flowp.testing module only
