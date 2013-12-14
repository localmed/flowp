Flowp 1.0
-----------
Flowp is a library which tries to bring the best ideas from Ruby / node.js
world to Python making development more fun. For version 1.0 module
flowp.testing is avaiable which allows to write tests in a RSpec BDD
style with minimum of magic.

.. note::

    Only Python >=3.3

Quick start
-----------
Put into spec_someobject.py:

..  code-block::python

    from flowp.testing import Behavior, when, expect
    from unittest import mock
    from mymodule import SomeObject

    class SomeObject(Behavior):
        def before_each(self):
            self.subject = SomeObject()

        def logger_given(self):
            self.logger = mock.Mock()
            self.subject = SomeObject(self.logger)

        def it_counts_positive_number(self):
            expect(self.subject(-1, 2, -3, 4)) == 2

        @when(logger_given)
        def it_sends_results_to_logger(self):
            expect(self.logger.info).called_with(2)

::

    $ pip install flowp
    $ python3 -m flowp.testing -v


flowp.testing
--------------
Characteristic:

* follow BDD style
* influenced by RSpec
* minimalistic
* with minimum of magic
* written on top of unittest


BDD style conventions:

* specifications
* expectations
* contexts


Specyfications
^^^^^^^^^^^^^
They are specify object behaviors, kind of replacement of test cases.

* each file which contains specifications should be prefixed with spec_*


Expectations
^^^^^^^^^^^^^^
Expectations are replacement of asserts.

.. autoclass:: expect
    :members:

Contexts
^^^^^^^^^^^^^^
It is possible to give contexts for specyfic behaviors by @when decorator.
Decorator can take as an argument generator or string. When it receive generator
it will treat it as a context manager, string will be only used for test runner
results.


.. code-block:: python

    class User(Behavior):
        def logged_as_admin(self):
            # do some before actions
            yield
            # do some after actions

        @when(logged_as_admin):
        def it_can_delete_posts(self):
            pass

        @when('executing login'):
        def it_rejects_not_registered(self):
            pass


'yield' statement define the border between setup/teardown actions,
like in contextlib.contextmanager module but for tests. Context method
can be without yield statement and it will behave like a setup context.

We can also check many contexts:

.. code-block:: python

    class User(Behavior):
        def executing_login(self):
            ...

        def user_not_registered(self):
            ...

        def user_registered(self):
            ...

        @when(executing_login, user_not_registered)
        def it_interrupts_process(self):
            ...

        @when(executing_login, user_registered)
        def it_pass_process(self):
            ...

Unfortunally behaviors with identical names will collide even if they
have different contexts in when decorator. For now there is no solution for
this.


Plans for the future
-----------
There are plans for 3 additional modules in version 2.0:

* flowp.ftypes - overwritted or additional data structures like List, Dict,
Str, DependencyGraph with extra methods.

* flowp.system - more convinient files manipulation

* flowp.task - universal task/package manager (infuenced by Rake, Yeoman,
Grunt, Fabric, Brew)

Each of them is already partly implemented.
