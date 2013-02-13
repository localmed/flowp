import flowp.testing
from flowp import types
from mock import patch
import unittest

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


class ListTest(flowp.testing.TestCase):
    def setUp(self):
        self.l = self.subject(types.List([1,2,3]))

    def test_type_transformation_properties(self):
        self.l.tuple.should == types.Tuple((1,2,3))
        self.l.set.should == types.Set([1,2,3])
        self.l.str.should == types.Str("[1, 2, 3]")

    def test_function_like_operator_properties(self):
        self.l.min.should == types.Int(1)
        self.l.max.should == types.Int(3)
        l2 = self.subject(types.List([True, False, True]))
        l3 = self.subject(types.List([True, True, True]))
        l4 = self.subject(types.List([False, False, False]))
#       l2.all.should.be_false
#       l3.all.should.be_true
#       l2.any.should.be_true
#       l4.any.should.be_false
        self.l.len.should == types.Int(3)
        self.l.sum.should == types.Int(6)

    def test_function_like_operator_methods(self):
        self.l.map(lambda x: x*2).should == types.List([2,4,6])
        self.l.filter(lambda x: x==2).should == types.List([1,3])
        self.l.reduce(lambda a,b: a+b).should == types.Int([6])
        lstr = types.List(['a', 'b', 'c'])
        lstr.join('-').should == types.Str("a-b-c")


class StrIntTest(flowp.testing.TestCase):
   def test_type_transformation_properties(self):
       some_int = self.subject(types.Int(3))
       some_str = self.subject(types.Str("2"))
       some_int.str.should == types.Str("3")
       some_str.int.should == types.Int(2)