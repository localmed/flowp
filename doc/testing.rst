flowp.testing
===============
Module allows to write tests in a RSpec BDD style with minimum of magic and
maximum of comfort.

Quick start
------------
Test subject (mymodule.py):

.. code-block:: python

    class Calculator:
        def __init__(self):
            self.special_mode = False

        def add(a, b):
            sum = a + b
            if self.special_mode:
                sum += 1
            return sum


Behavior specification (spec_mymodule.py):

..  code-block:: python

    import mymodule
    from flowp.testing import Behavior, expect


    class Calculator(Behavior):
        def before_each(self):
            self.subject = mymodule.Calculator()

        def it_add_numbers(self):
            expect(self.subject(1, 2)) == 3

        class WhenHaveSpecialMode(Behavior):
            def before_each(self):
                self.subject.special_mode = True

            it_add_additional_one(self):
                expect(self.subject(1, 2)) == 4

::

    $ python3 -m flowp.testing --watch

Giving --watch flag script will be watching on specification files, if
some changes happen, tests will be reran.

Expectations
-------------
Expectations are replacement of asserts. They provide better feedback than asserts,
similar to self.assert* methods, but they are shorter and easier to remember.
Example of expectation::

    expect(subject) == expected_value

::

    expect(subject, 'message for failure') == expected_value


Basic expectations
^^^^^^^^^^^^^^^^^^^

==================================== ===============================
expectation                          corresponding assert
==================================== ===============================
expect(a).to_be(True)                assert a
expect(a).to_be(False)               assert not a
expect(a) == b                       assert a == b
expect(a) != b                       assert a != b
expect(a) < b                        assert a < b
expect(a) > b                        assert a > b
expect(a) >= b                       assert a >= b
expect(a) <= b                       assert a <= b
expect(a).to_be(b)                   assert a is b
expect(a).not_to_be(b)               assert a is not b
expect(a).to_be_in(b)                assert a in b
expect(a).not_to_be_in(b)            assert a not in b
expect(a).to_be_instance_of(b)       assert isinstance(a, b)
expect(a).not_to_be_instance_of(b)   assert not isinstance(a, b)
==================================== ===============================


Exception expectation
^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

    with expect.to_raise(AssertionError):
        assert 1 == 2




Custom expectations
^^^^^^^^^^^^^^^^^^^^^

You can also create Your own expectations. 'expect' is a normal class
(but with lowercased name), which implements methods such a '__eq__' or
'ok', so You can write Your own expect class by inheriting from the
original one.

.. code-block:: python

    from flowp import testing

    class expect(testing.expect):
        def is_equal_to(self, expectation):
            assert self._context == expectation,\
                "expected %s, given %s" % (expectation, self._context)


::

    expect(2).is_equal_to(2)


Behaviors
--------------

Behaviors are the containers for tests.
Each of them should describe an object or special context which we want to test.

Behaviors can be nested, in that case during each test
execution current and all of upper before / after methods will be executed
with the 'self' context of tested behavior.

Draft of execution process for nested test:

.. code-block:: python

    b2 = B2()

    B1.before_each(b2)
    b2.before_each()
    b2.it_method()
    b2.after_each()
    B1.after_each(b2)

Example of structure:

.. code-block:: python

    class B1(Behavior):
        def before_each(self):
            pass

        def after_each(self):
            pass

        class B2(Behavior):
            def before_each(self):
                pass

            def after_each(self):
                pass

            def it_method(self):
                pass

Runner
--------
Tests can be easily run by command::

    $ python3 -m flowp.testing

Runner will be looking for 'spec_*.py' files in the current directory and its subdirectories
and then for Behavior subclasses. Methods which name starts with 'it_' will
be treated as test methods.

@skip
^^^^^^^

Skips tests. Can be used on behavior class or test method.

@only
^^^^^^^
Opposite of skip. It will execute behaviors or methods which have @only decorator rest
will be skipped.


Mocking
--------
flowp.testing module is compatible with unittest.mock
Very simple mocking:

* self.mock is a mocks factory
* it returns MagicMock each time as default
* it can be used as patcher if first argument given
  (mock factory holds reference and it will unpatch mock after each test)
* have type arg (type='magicmock')
* work as patch.object: self.mock(object, 'attr_name')

.. code-block:: python

    class MyObject(Behavior):
        def before_each(self):
            self.mocked_logger = self.mock('logger')

        def it_do_some_stuff(self):
            ...

::

    self.mock('time.time')

::

    self.mock(obj, 'attr_name')

::

    self.mock(target=None, attr=None, spec=None, new=None)


Mock expectations
^^^^^^^^^^^^^^^^^^

======================================== ===============================
expectation                              corresponding assert
======================================== ===============================
expect(m).to_have_been_called()          assert m.called
expect(m).to_have_been_called(n)         assert m.call_count == n
expect(m).not_to_have_been_called()      assert not m.called
expect(m).to_have_been_called_with(...)  m.assert_any_cal(...)
======================================== ===============================


Files testing
---------------
Example:

.. code-block:: python

    from flowp.testing import FilesBehavior, expect
    from flowp.files import touch, exist

    class Touch(FilesBehavior):
        def before_each(self):
            super().before_each()
            # do some preparations

        def it_create_file(self):
            touch('testfile')
            expect(exist('testfile')).to_be(True)

.. autoclass:: flowp.testing.FileSystemBehavior
    :members: before_each, after_each, reset_cwd
