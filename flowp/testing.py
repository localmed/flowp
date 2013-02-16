import unittest
import re


class BDDTestCase(type):
    def __new__(cls, name, bases, namespace, **kwargs):
        new_namespace = {}
        for key, value in namespace.items():
            if key.startswith('it_'):
                key = re.sub('^it_', 'test_it_', key)

            if key == 'before_each':
                key = 'setUp'

            if key == 'after_each':
                key = 'tearDown'

            new_namespace[key] = value

        return type.__new__(cls, name, bases, new_namespace)


class TestCase(unittest.TestCase, metaclass=BDDTestCase):

    def subject(self, someobject):
        pass
