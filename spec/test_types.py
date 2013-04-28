import mock
import flowp.typess
from flowp.testing import Behavior


class SomeTest(Behavior):
    def it_do_something(self):
        pass


class Should(Behavior):
    class Int(int):
        pass

    class Bool(object):
        def __init__(self, value):
            self.value = value

        def __bool__(self):
            return self.value

    class List(list):
        pass

    class NoneType(object):
        def __init__(self):
            self.value = None

    def before_each(self):
        self.int = self.Int(1)
        self.int.should = flowp.typess.Should(self.int)
        self.true = self.Bool(True)
        self.true.should = flowp.typess.Should(self.true)
        self.false = self.Bool(False)
        self.false.should = flowp.typess.Should(self.false)
        self.list = self.List([1, 2, 3])
        self.list.should = flowp.typess.Should(self.list)
        self.none = self.NoneType()
        self.none.should = flowp.typess.Should(self.none)

    def it_do_correct_should_asserts(self):
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

    def it_do_not_correct_should_asserts(self):
        with self.assertRaises(AssertionError):
            self.int.should == 2


class Object(Behavior):
    class SomeClass(flowp.typess.Object):
        x = 1

    def before_each(self):
        self.object = flowp.typess.Object()

    def it_have_should_object(self):
        assert isinstance(self.object.should, flowp.typess.Should)
        assert self.object.should.context is self.object

    def it_have_type_property(self):
        assert self.object.type is flowp.typess.Object
        assert self.object.type is not object

    def it_have_is_callable_property(self):
        class Callable(flowp.typess.Object):
            def __call__(self):
                return True

        assert not self.object.is_callable
        assert Callable().is_callable

    def it_have_is_instanceof_method(self):
        assert self.object.is_instanceof(flowp.typess.Object)

    def it_have_hasattr_method(self):
        ob = self.SomeClass()
        assert ob.hasattr('x')
        assert not ob.hasattr('y')

    def it_have_getattr_method(self):
        ob = self.SomeClass()
        assert ob.getattr('x') == 1


class Iterable(Behavior):
    class Tuple(tuple, flowp.typess.Iterable):
        pass

    def before_each(self):
        self.tuple1 = self.Tuple((1, 2, 3))
        self.tuple2 = self.Tuple((True, True, True))
        self.tuple3 = self.Tuple((True, False, True))
        self.tuple4 = self.Tuple((False, False, False))

    def it_have_len_property(self):
        assert self.tuple1.len == 3

    def it_have_all_property(self):
        assert self.tuple2.all
        assert not self.tuple3.all

    def it_have_any_property(self):
        assert self.tuple2.any
        assert self.tuple3.any
        assert not self.tuple4.any

    def it_have_min_property(self):
        assert self.tuple1.min == 1

    def it_have_max_property(self):
        assert self.tuple1.max == 3

    def it_have_sum_property(self):
        assert self.tuple1.sum == 6

    def it_have_map_method(self):
        self.tuple1.map(lambda x: 2*x) == self.Tuple((2, 4, 6))

    def it_have_filter_method(self):
        self.tuple1.filter(lambda x: x in (1, 3)) == self.Tuple((1, 3))

    def it_have_reduce_method(self):
        self.tuple1.reduce(lambda a, b: a*b) == 6


class TypesPropagator(Behavior):
    class SomeClass(flowp.typess.TypesPropagator):
        cls_att = 'cls_att'

        def __init__(self):
            self.obj_att = 'obj_att'

        def some_method(self):
            return "abc"

    def before_each(self):
        self.obj = self.SomeClass()

    @mock.patch('flowp.typess.this')
    def it_pass_every_attribute_lookup_value_through_this_function(self, this_mock):
        self.obj.cls_att
        this_mock.assert_called_with('cls_att')
        self.obj.obj_att
        this_mock.assert_called_with('obj_att')


class ThisMethod(Behavior):
    def it_transforms_builtin_types_to_flowp_types(self):
        assert isinstance(flowp.typess.this(1), flowp.typess.Int)
        assert isinstance(flowp.typess.this(1.1), flowp.typess.Float)
        assert isinstance(flowp.typess.this("abc"), flowp.typess.Str)
        assert isinstance(flowp.typess.this(True), flowp.typess.BoolProxy)
        assert isinstance(flowp.typess.this(None), flowp.typess.NoneProxy)
        assert isinstance(flowp.typess.this([1, 2, 3]), flowp.typess.List)
        assert isinstance(flowp.typess.this((1, 2, 3)), flowp.typess.Tuple)
        assert isinstance(flowp.typess.this({'a': 1, 'b': 2}), flowp.typess.Dict)
        assert isinstance(flowp.typess.this({1, 2, 3}), flowp.typess.Set)

    def it_transform_function_types_to_flowp_function_types(self):
        class SomeClass:
            def method(self):
                return 1

        def function():
            return 2

        obj = SomeClass()
        assert isinstance(flowp.typess.this(function), flowp.typess.FunctionProxy)
        assert isinstance(flowp.typess.this(obj.method), flowp.typess.FunctionProxy)
        assert isinstance(flowp.typess.this("abc".index), flowp.typess.FunctionProxy)

    def it_add_flowp_object_class_as_mixin_if_not_builtin_type(self):
        class SomeClass:
            pass

        obj = SomeClass()
        obj.a = 111
        assert isinstance(flowp.typess.this(obj), flowp.typess.Object)
        assert isinstance(flowp.typess.this(obj), SomeClass)
        assert obj.a == 111
        assert hasattr(obj, 'should')


class ObjectProxy(Behavior):
    def before_each(self):
        self.subject = "abc"
        self.obj = flowp.typess.ObjectProxy(self.subject)

    def it_stores_subject_at_subject_attribute(self):
        assert self.obj.subject is self.subject

    def it_pass_lookup_to_subject_attributes(self):
        assert self.obj.index("c") == 2

    def it_pass_lookup_to_subject_property_attributes(self):
        class SomeClass:
            @property
            def prop(self):
                return 1

        obj = flowp.typess.ObjectProxy(SomeClass())
        assert obj.prop == 1



class FunctionProxy(Behavior):
    def before_each(self):
        def func(x):
            return x

        func.someatt = 1
        self.fproxy = flowp.typess.FunctionProxy(func)

    def it_is_callable(self):
        assert self.fproxy(1) == 1
        assert self.fproxy("abc") == "abc"

    def it_lookup_to_function_attributes(self):
        assert self.fproxy.someatt == 1
