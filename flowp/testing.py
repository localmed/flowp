import unittest
import types

class TestCase(unittest.TestCase):

    EXTENDABLE_BUILTIN_TYPES = (int,float,str,list,tuple,dict)

    def subject(self, someobject):
        """
        Create Should object at should property of given object. If object is built-in type,
        create class that inherits from that built-in, and transform given object to that class (it is needed
        if we want to set should property to built-in).
        """
        # Decorator for methods
        def function_subject(decfunc):
            def _newfunc(*args, **kwargs):
                return self.subject(decfunc(*args, **kwargs))

            return _newfunc

        # Do not decorate these objects
        # bool object is not extendable type, so can not have should property
        # type object decorating is not needed for now
        if type(someobject) in (bool, type):
            return someobject

        # Decorate methods objects
        if type(someobject) in (types.MethodType, types.FunctionType, types.BuiltinMethodType):
            return function_subject(someobject)

        # Create wrapper class if built-in type object
        if type(someobject) in self.EXTENDABLE_BUILTIN_TYPES:
            classname = 'T' + type(someobject).__name__
            BuiltinWrapperClass = type(classname, (type(someobject), ), {})
            someobject = BuiltinWrapperClass(someobject)
        else:
            # Decorate elements in object dictionary, do self.subject on every element (recursion step)
            for elName in dir(someobject):
                # Pass deep private methods
                if elName.startswith('__'):
                    continue

                descrEl = getattr(someobject, elName)
                setattr(someobject, elName, self.subject(descrEl))


        # Set Should object to should property
        someobject.should = Should(someobject, self)
        return someobject

class Should:
    """
    Should object is set by TestCase.subject method. Each method of Should object
    is kind a unittest.TestCase assert.
    """
    def __init__(self, context, testcase:TestCase):
        """
        Construct Should object
        @param context: context of Should object
        @param testcase: Reference to TestCase object
        """
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