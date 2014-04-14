flowp.doo
===============

Quick start
-------------

Create file doofile.py:

.. code-block:: python

    from flowp import doo

    class Default(doo.Namespace):
        def hello(self, name=""):
            print("Hello %s!" % name)

In the same directory run task script from command line:

.. code-block:: bash

    $ doo hello
    Hello !
    $ doo hello:world
    Hello world!


Namespacing
-------------------

.. code-block:: python

    from flowp import doo


    class Nm1(doo.Namespace):
        def __call__(self):
            print("Hello 0")

        def hello(self):
            print("Hello 1")

        class Nm2(doo.Namespace):
            def hello(self, who="2"):
                Nm1().hello()
                print("Hello " + who)


.. code-block:: bash

    $ doo nm1
    Hello 0
    $ doo nm1::hello
    Hello 1
    $ doo nm1::nm2::hello
    Hello 1
    Hello 2
    $ doo nm1::nm2::hello:world
    Hello 1
    Hello world
