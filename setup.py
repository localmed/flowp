"""
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



Quick start
-----------
Test subject (mymodule.py):

.. code-block:: python

    class Calculator:
        def __init__(self):
            self.special_mode = False

        def add(self, a, b):
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
            expect(self.subject.add(1, 2)) == 3

        class WhenHaveSpecialMode(Behavior):
            def before_each(self):
                self.subject.special_mode = True

            def it_add_additional_one(self):
                expect(self.subject.add(1, 2)) == 4

::

    $ python3 -m flowp.testing --watch

Giving --watch flag script will be watching on python files, if
some changes happen, tests will be reran.


Documentation
---------------

http://pawelgalazka.github.io/flowp/
"""
from distutils.core import setup

setup(
    name='flowp',
    version='1.1',
    description='More fun with Python development',
    long_description=__doc__,
    url='http://flowp.readthedocs.org/en/latest/',
    license='BSD',
    author='Pawel Galazka',
    author_email='pawel.galazka@pracli.com',
    packages=['flowp'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development',
        'Topic :: Software Development :: Testing'
    ]
)
