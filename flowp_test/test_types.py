import mock
import flowp.types
import flowp.testing


class DescribeShould(flowp.testing.TestCase):
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

    def before_each(self):
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


class DescribeObject(flowp.testing.TestCase):
    class SomeClass(flowp.types.Object):
        x = 1

    def before_each(self):
        self.object = flowp.types.Object()

    def it_have_should_object(self):
        assert isinstance(self.object.should, flowp.types.Should)
        assert self.object.should.context is self.object

    def it_have_type_property(self):
        assert self.object.type is flowp.types.Object
        assert self.object.type is not object

    def it_have_is_callable_property(self):
        class Callable(flowp.types.Object):
            def __call__(self):
                return True

        assert not self.object.is_callable
        assert Callable().is_callable

    def it_have_is_instanceof_method(self):
        assert self.object.is_instanceof(flowp.types.Object)

    def it_have_hasattr_method(self):
        ob = self.SomeClass()
        assert ob.hasattr('x')
        assert not ob.hasattr('y')

    def it_have_getattr_method(self):
        ob = self.SomeClass()
        assert ob.getattr('x') == 1


class DescribeIterable(flowp.testing.TestCase):
    class Tuple(tuple, flowp.types.Iterable):
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


class DescribeTypesPropagator(flowp.testing.TestCase):
    class SomeClass(flowp.types.TypesPropagator):
        cls_att = 'cls_att'

        def __init__(self):
            self.obj_att = 'obj_att'

        def some_method(self):
            return "abc"

    def before_each(self):
        self.obj = self.SomeClass()

    @mock.patch('flowp.types.this')
    def it_pass_every_attribute_lookup_value_through_this_function(self, this_mock):
        self.obj.cls_att
        this_mock.assert_called_with('cls_att')
        self.obj.obj_att
        this_mock.assert_called_with('obj_att')


class DescribeThisMethod(flowp.testing.TestCase):
    def it_transforms_builtin_types_to_flowp_types(self):
        assert isinstance(flowp.types.this(1), flowp.types.Int)
        assert isinstance(flowp.types.this(1.1), flowp.types.Float)
        assert isinstance(flowp.types.this("abc"), flowp.types.Str)
        assert isinstance(flowp.types.this(True), flowp.types.BoolProxy)
        assert isinstance(flowp.types.this(None), flowp.types.NoneProxy)
        assert isinstance(flowp.types.this([1, 2, 3]), flowp.types.List)
        assert isinstance(flowp.types.this((1, 2, 3)), flowp.types.Tuple)
        assert isinstance(flowp.types.this({'a': 1, 'b': 2}), flowp.types.Dict)
        assert isinstance(flowp.types.this({1, 2, 3}), flowp.types.Set)

    def it_transform_function_types_to_flowp_function_types(self):
        class SomeClass:
            def method(self):
                return 1

        def function():
            return 2

        obj = SomeClass()
        assert isinstance(flowp.types.this(function), flowp.types.FunctionProxy)
        assert isinstance(flowp.types.this(obj.method), flowp.types.FunctionProxy)
        assert isinstance(flowp.types.this("abc".index), flowp.types.FunctionProxy)

    def it_add_flowp_object_class_as_mixin_if_not_builtin_type(self):
        class SomeClass:
            pass

        obj = SomeClass()
        obj.a = 111
        assert isinstance(flowp.types.this(obj), flowp.types.Object)
        assert isinstance(flowp.types.this(obj), SomeClass)
        assert obj.a == 111
        assert hasattr(obj, 'should')


class DescribeObjectProxy(flowp.testing.TestCase):
    def before_each(self):
        self.subject = "abc"
        self.obj = flowp.types.ObjectProxy(self.subject)

    def it_stores_subject_at_subject_attribute(self):
        assert self.obj.subject is self.subject

    def it_pass_lookup_to_subject_attributes(self):
        assert self.obj.index("c") == 2

    def it_pass_lookup_to_subject_property_attributes(self):
        class SomeClass:
            @property
            def prop(self):
                return 1

        obj = flowp.types.ObjectProxy(SomeClass())
        assert obj.prop == 1



class DescribeFunctionProxy(flowp.testing.TestCase):
    def before_each(self):
        def func(x) -> "Annotation":
            return x

        func.someatt = 1
        self.fproxy = flowp.types.FunctionProxy(func)

    def it_is_callable(self):
        assert self.fproxy(1) == 1
        assert self.fproxy("abc") == "abc"

    def it_lookup_to_function_attributes(self):
        assert self.fproxy.__annotations__ == {'return': 'Annotation'}
        assert self.fproxy.someatt == 1
