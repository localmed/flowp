flowp.task
===============
Module provides simple framework for universal task management. At this point
it can be used either for building process, package management or scaffolding.

Quick start
-------------

Create file taskfile.py:

.. code-block:: python

    from flowp import task

    class Main(task.Plugin):
        def hello(self, name=""):
            print("Hello %s!" % name)

In the same directory run task script from command line:

.. code-block:: bash

    $ task hello
    Hello !
    $ task hello:world
    Hello world!

Components
-------------
.. autoclass:: flowp.task.Plugin

.. autoclass:: flowp.task.Script



Namespacing
-------------------

.. code-block:: python

    from flowp import task


    class Nm2(task.Plugin):
        def hello(self, who="2"):
            print("Hello " + who)

    class Nm1(task.Plugin):
        nm2 = Nm2()

        def __call__(self):
            print("Hello 0")

        def hello(self):
            print("Hello 1")

    class Main(task.Plugin):
        nm1 = Nm1()

.. code-block:: bash

    $ task nm1
    Hello 0
    $ task nm1::hello
    Hello 1
    $ task nm1::nm2::hello
    Hello 2
    $ task nm1::nm2::hello:world
    Hello world

Dependencies
-------------------

.. code-block:: python

    from flowp import task

    class TaskFile(task.Plugin):
        def t1(self):
            print('T1')

        @task.require(t1)
        def t2(self):
            print('T2')

        @task.require(t1, t2)
        def t3(self):
            print('T3')


.. code-block:: bash

    $ task t3
    T1
    T2
    T3


Builtin plugins
----------------
sdfsf

Install
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Invoking:

.. code-block:: bash

    $ task install:web.jquery
    $ task install:py.flask
    $ task install::list
    $ task install::search:jquery
    $ task uninstall:py.flask

Package formula searching algorithm (web.jquery):

#. .task/packages/web/jquery.py
#. $HOME/.task/packages/web/jquery.py

Package formula (jquery.py):

.. code-block:: python

    class Main(task.packages.web.Package):
        def install(self):
            ...

        def uninstall(self):
            ...

When invoking with no arguments:

.. code-block:: bash

    $ task install

it reads packages info from install_requires variable
from taskfile.py

.. code-block:: python

    install_packages = []

Scaffold
^^^^^^^^^^^^^^^^^^^^^^^^^


.. code-block:: bash

    $ task scaffold::webapp


.. code-block:: python

    from system import TaskFile, cp

    class TaskFile(system.TaskFile):
        tmpl = Template('/some/path/templates1')

        
        def genagnular(self, type):
            if type == 'controller':
                cp(self.tmpl('ctrl_pattern.js'), 'controller.js')
