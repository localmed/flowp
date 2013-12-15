"""
Flowp 1.0
==========
Flowp is a library which tries to bring the best ideas from Ruby / node.js
world to Python making development more fun. For version 1.0 module
flowp.testing is avaiable which allows to write tests in a RSpec BDD
style with minimum of magic.

Installation
------------
::

    $ pip3 install flowp

.. note::

    Only for Python >=3.3


Quick start
-----------
Test subject (mymodule.py):

.. code-block:: python

    class SomeObject:
        def __init__(self, logger=None):
            self._logger = logger

        def count(self, *args):
            positives = 0
            for arg in args:
                if arg < 0:
                    positives += 1

            if self._logger:
                self._logger.info(positives)
            else:
                return positives


Behavior specyfication (spec_mymodule.py):

..  code-block:: python

    import mymodule
    from flowp.testing import Behavior, when, expect
    from unittest import mock


    class SomeObject(Behavior):
        def before_each(self):
            self.subject = mymodule.SomeObject()

        def logger_given(self):
            self.logger = mock.Mock()
            self.subject = mymodule.SomeObject(self.logger)

        def it_counts_positive_numbers(self):
            expect(self.subject.count(-1, 2, -3, 4)) == 2

        @when(logger_given)
        def it_sends_results_to_logger(self):
            self.subject.count(-1, 2, -3, 4)
            expect(self.logger.info).called_with(2)

::

    $ python3 -m flowp.testing -v
"""
from distutils.core import setup

setup(
    name='flowp',
    version='1.0',
    description='More fun with Python development',
    url='https://github.com/pawelgalazka/flowp',
    license='BSD',
    author='Pawel Galazka',
    author_email='pawel.galazka@pracli.com',
    packages=['flowp'],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development',
        'Topic :: Software Development :: Testing'
    ]
)
