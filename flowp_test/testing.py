import unittest
import flowp.testing
from mock import patch

class TestCaseIntegrationTest(flowp.testing.TestCase):
    class Something:
        def __init__(self):
            self.a = 1
            self.b = "abc"

        def c(self):
            return "def"

    def test_subject_declaration_add_should_object(self):
        subject = "abc"
        subject = self.subject(subject)
        self.assertIsInstance(subject.should, flowp.testing.Should)

    def test_subject_declaration_add_should_object_to_every_element_in_object_descriptor(self):
        subject = self.Something()
        subject = self.subject(subject)
        self.assertIsInstance(subject.a.should, flowp.testing.Should)
        self.assertIsInstance(subject.b.should, flowp.testing.Should)
        self.assertIsInstance(subject.c().should, flowp.testing.Should)

    def test_should_asserts_with_subject_declaration(self):
        sub = self.Something()
        sub = self.subject(sub)
        sub.should.be_instanceof(self.Something)
        sub.a.should.be_instanceof(int)
        sub.a.should == 1
        sub.c().should.be_instanceof(str)
        sub.c().should == "def"

    def test_truefalse_should_asserts_with_subject_declaration(self):
        """
        TODO: This test fails, bool objects (True, False) are not extendable types,
        so they are kind a problematic at this point. Needed different solution.
        """
        true_sub = self.subject(True)
        false_sub = self.subject(False)
        true_sub.should.be_true
        false_sub.should.be_false


class ShouldTest(unittest.TestCase):
    class Str(str):
        pass

    class Int(int):
        pass

    class Bool:
        def __init__(self, value:bool):
            self.value = value

        def __bool__(self):
            return self.value

    def setUp(self):
        self.context = self.Str("abcd")
        self.context.should = flowp.testing.Should(self.context, self)

    def test_create_should_object_with_context_objects(self):
        self.assertIsInstance(self.context.should, flowp.testing.Should)

    def test_do_equal_should_assert(self):
        with patch.object(self, 'assertEqual') as mock_method:
            self.context.should == "abc"

        mock_method.assert_called_with(self.context, 'abc')

    def test_do_notequal_should_assert(self):
        with patch.object(self, 'assertNotEqual') as mock_method:
            self.context.should != 'abcd'

        mock_method.assert_called_with(self.context, 'abcd')

    def test_do_truefalse_should_assert(self):
        context = self.Bool(True)
        context.should = flowp.testing.Should(context, self)

        with patch.object(self, 'assertTrue') as mock_method:
            context.should.be_true

        mock_method.assert_called_with(context)

        with patch.object(self, 'assertFalse') as mock_method:
            context.should.be_false

        mock_method.assert_called_with(context)

    def test_do_is_should_assert(self):
        with patch.object(self, 'assertIs') as mock_method:
            self.context.should.be('abcd')

        mock_method.assert_called_once_with(self.context, 'abcd')

    def test_do_notis_should_assert(self):
        with patch.object(self, 'assertIsNot') as mock_method:
            self.context.should.not_be('abcd')

        mock_method.assert_called_once_with(self.context, 'abcd')

    def test_do_in_should_assert(self):
        context = self.Int(1)
        context.should = flowp.testing.Should(context, self)
        with patch.object(self, 'assertIn') as mock_method:
            context.should.be_in([1,2,3])

        mock_method.assert_called_once_with(context, [1,2,3])

    def test_do_notin_should_assert(self):
        context = self.Int(1)
        context.should = flowp.testing.Should(context, self)
        with patch.object(self, 'assertNotIn') as mock_method:
            context.should.not_be_in([2,3,4])

        mock_method.assert_called_once_with(context, [2,3,4])

    def test_do_isinstance_should_assert(self):
        with patch.object(self, 'assertIsInstance') as mock_method:
            self.context.should.be_instanceof(str)

        mock_method.assert_called_once_with(self.context, str)

    def test_do_isnotinstance_should_assert(self):
        with patch.object(self, 'assertNotIsInstance') as mock_method:
            self.context.should.not_be_instanceof(str)

        mock_method.assert_called_once_with(self.context, str)

    def test_do_greater_less_should_assert(self):
        one = self.Int(1)
        two = self.Int(2)
        one.should = flowp.testing.Should(one, self)
        two.should = flowp.testing.Should(two, self)
        with patch.object(self, 'assertLess') as mock_method:
            one.should < two

        mock_method.assert_called_with(one, two)

        with patch.object(self, 'assertGreater') as mock_method:
            one.should > two

        mock_method.assert_called_with(one, two)
