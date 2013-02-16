import flowp.types
import unittest


class ShouldTest(unittest.TestCase):
    class Int(int):
        pass

    class Bool:
        def __init__(self, value):
            self.value = value

        def __bool__(self):
            return self.value

    class List(list):
        pass

    class NoneType:
        def __init__(self):
            self.value = None

    def setUp(self):
        self.int = self.Int(1)
        self.int.should = flowp.types.Should(self.int)
        self.true = self.Bool(True)
        self.true.should = flowp.types.Should(self.true)
        self.false = self.Bool(False)
        self.false.should = flowp.types.Should(self.false)
        self.list = self.List([1, 2, 3])
        self.list.should = flowp.types.Should(self.list)
        self.none = self.NoneType()
        self.none.should = flowp.types.Should(self.none)

    def test_should_correct_asserts(self):
        self.int.should.be_instanceof(self.Int)
        self.int.should == 1
        self.int.should != 2
        self.int.should < 2
        self.int.should <= 1
        self.int.should > 0
        self.int.should >= 1
        self.int.should.be(self.int)
        self.int.should.not_be(1)
        self.true.should.be_true
        self.false.should.be_false
        self.none.should.be_none
        self.int.should.be_in([1, 2, 3])
        self.int.should.not_be_in([2, 3, 4])
        self.int.should.be_instanceof(self.Int)
        self.int.should.not_be_instanceof(self.Bool)

    def test_should_not_correct_asserts(self):
        with self.assertRaises(AssertionError):
            self.int.should == 2


class ObjectTest(unittest.TestCase):
    def setUp(self):
        self.object = flowp.types.Object()

    def test_have_should_object(self):
        assert isinstance(self.object.should, flowp.types.Should)
        assert self.object.should.context is self.object

    def test_have_type_property(self):
        assert self.object.type is flowp.types.Object

    def test_have_is_callable_property(self):
        class Callable(flowp.types.Object):
            def __call__(self):
                return True

        assert not self.object.is_callable
        assert Callable().is_callable

    def test_have_is_instanceof_method(self):
        assert self.object.is_instanceof(flowp.types.Object)

    def test_have_is_subclassof_method(self):
        class Class(flowp.types.Object):
            pass

        assert Class.is_subclassof(flowp.types.Object)
