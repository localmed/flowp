import unittest
import types

class TestCase(unittest.TestCase):

    EXTENDABLE_BUILTIN_TYPES = (int,float,str,list,tuple,object,type)

    def subject(self, someobject):
        """
        Create Should object at should property of given object. If object is built-in type,
        create class that inherits from that built-in, and transform given object to that class (it is needed
        if we want to set should property to built-in).
        """
        def _function_subject(decfunc):
            def _newfunc(*args, **kwargs):
                return self.subject(decfunc(*args, **kwargs))

            return _newfunc

        # Bool object is not extendable type, so can not have should property
        if type(someobject) is bool:
            return someobject

        # Create wrapper class if built-in type object
        if type(someobject) in self.EXTENDABLE_BUILTIN_TYPES:
            classname = 'T' + type(someobject).__name__
            BuiltinWrapperClass = type(classname, (type(someobject), ), {})
            someobject = BuiltinWrapperClass(someobject)

        else:
            # Wrap elements in object descriptor, do self.subject in recursion
            for elName in dir(someobject):
                if elName.startswith('__'):
                    continue

                descrEl = getattr(someobject, elName)

                # if function, decorate return values
                if type(descrEl) is types.MethodType:
                    setattr(someobject, elName, self.subject(_function_subject(descrEl)))
                else:
                    setattr(someobject, elName, self.subject(descrEl))


        # Set Should object to should property
        someobject.should = Should(someobject, self)
        return someobject

class Should:
    def __init__(self, context, testcase:TestCase):
        self.context = context
        self.testcase = testcase

    def __eq__(self, other):
        self.testcase.assertEqual(self.context, other)

    def __ne__(self, other):
        self.testcase.assertNotEqual(self.context, other)

    def __lt__(self, other):
        self.testcase.assertLess(self.context, other)

    def __le__(self, other):
        self.testcase.assertLessEqual(self.context, other)

    def __gt__(self, other):
        self.testcase.assertGreater(self.context, other)

    def __ge__(self, other):
        self.testcase.assertGreaterEqual(self.context, other)

    def be(self, other):
        self.testcase.assertIs(self.context, other)

    def not_be(self, other):
        self.testcase.assertIsNot(self.context, other)

    @property
    def be_true(self):
        self.testcase.assertTrue(self.context)

    @property
    def be_false(self):
        self.testcase.assertFalse(self.context)

    def be_in(self, other):
        self.testcase.assertIn(self.context, other)

    def not_be_in(self, other):
        self.testcase.assertNotIn(self.context, other)

    def be_instanceof(self, other):
        self.testcase.assertIsInstance(self.context, other)

    def not_be_instanceof(self, other):
        self.testcase.assertNotIsInstance(self.context, other)