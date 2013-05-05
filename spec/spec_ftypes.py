import mock
from flowp import ftypes
from flowp.testing import Behavior


class Should(Behavior):
    def before_each(self):
        class Int(int):
            pass

        class Bool(object):
            def __init__(self, subject):
                self.subject = subject

            def __bool__(self):
                return self.subject

        class List(list):
            pass

        class NoneType(object):
            def __init__(self):
                self.value = None

        self.Int = Int
        self.Bool = Bool
        self.int = Int(1)
        self.int.should = ftypes.Should(self.int)
        self.true = Bool(True)
        self.true.should = ftypes.Should(self.true)
        self.false = Bool(False)
        self.false.should = ftypes.Should(self.false)
        self.list = List([1, 2, 3])
        self.list.should = ftypes.Should(self.list)
        self.none = NoneType()
        self.none.should = ftypes.Should(self.none)

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

    def it_do_should_raise_assert(self):
        def func():
            raise Exception()

        func.should = ftypes.Should(func) 
        func.should.throw(Exception).by_call()


class Object(Behavior):
    class SomeClass(ftypes.Object):
        x = 1

    def before_each(self):
        self.object = ftypes.Object()

    def it_have_should_object(self):
        assert isinstance(self.object.should, ftypes.Should)
        assert self.object.should.context is self.object

    def it_have_type_property(self):
        assert self.object.type is ftypes.Object
        assert self.object.type is not object

    def it_have_is_callable_property(self):
        class Callable(ftypes.Object):
            def __call__(self):
                return True

        assert not self.object.is_callable
        assert Callable().is_callable

    def it_have_is_instanceof_method(self):
        assert self.object.is_instanceof(ftypes.Object)

    def it_have_hasattr_method(self):
        ob = self.SomeClass()
        assert ob.hasattr('x')
        assert not ob.hasattr('y')

    def it_have_getattr_method(self):
        ob = self.SomeClass()
        assert ob.getattr('x') == 1
    
    def it_have_default_should_class_as_attribute(self):
        assert issubclass(self.object.Should, ftypes.Should)


class Iterable(Behavior):
    class Tuple(tuple, ftypes.Iterable):
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

    def it_have_min_max_properties(self):
        assert self.tuple1.min == 1
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
    class SomeClass(ftypes.TypesPropagator):
        cls_att = 'cls_att'

        def __init__(self):
            self.obj_att = 'obj_att'

        def some_method(self):
            return "abc"

    def before_each(self):
        self.obj = self.SomeClass()

    @mock.patch('flowp.ftypes.this')
    def it_pass_every_attribute_lookup_value_through_this_function(self, this_mock):
        self.obj.cls_att
        this_mock.assert_called_with('cls_att')
        self.obj.obj_att
        this_mock.assert_called_with('obj_att')


class ThisMethod(Behavior):
    def it_transforms_builtin_types_to_flowp_types(self):
        assert isinstance(ftypes.this(1), ftypes.Int)
        assert isinstance(ftypes.this(1.1), ftypes.Float)
        assert isinstance(ftypes.this("abc"), ftypes.Str)
        assert isinstance(ftypes.this(True), ftypes.BoolProxy)
        assert isinstance(ftypes.this(None), ftypes.NoneProxy)
        assert isinstance(ftypes.this([1, 2, 3]), ftypes.List)
        assert isinstance(ftypes.this((1, 2, 3)), ftypes.Tuple)
        assert isinstance(ftypes.this({'a': 1, 'b': 2}), ftypes.Dict)
        assert isinstance(ftypes.this({1, 2, 3}), ftypes.Set)

    def it_transform_function_types_to_flowp_function_types(self):
        class SomeClass(object):
            def method(self):
                return 1

        def function():
            return 2

        obj = SomeClass()
        assert isinstance(ftypes.this(function), ftypes.FunctionProxy)
        assert isinstance(ftypes.this(obj.method), ftypes.FunctionProxy)
        assert isinstance(ftypes.this("abc".index), ftypes.FunctionProxy)

    def it_add_flowp_object_class_as_mixin_if_not_builtin_type(self):
        class SomeClass(object):
            pass

        obj = SomeClass()
        obj.a = 111
        assert isinstance(ftypes.this(obj), ftypes.Object)
        assert isinstance(ftypes.this(obj), SomeClass)
        assert obj.a == 111
        assert hasattr(obj, 'should')


class ObjectProxy(Behavior):
    def before_each(self):
        self.subject = "abc"
        self.obj = ftypes.ObjectProxy(self.subject)

    def it_stores_subject_at_subject_attribute(self):
        assert self.obj.subject is self.subject

    def it_pass_lookup_to_subject_attributes(self):
        assert self.obj.index("c") == 2

    def it_pass_lookup_to_subject_property_attributes(self):
        class SomeClass(object):
            @property
            def prop(self):
                return 1

        obj = ftypes.ObjectProxy(SomeClass())
        assert obj.prop == 1



class FunctionProxy(Behavior):
    def before_each(self):
        def func(x):
            return x

        func.someatt = 1
        self.fproxy = ftypes.FunctionProxy(func)

    def it_is_callable(self):
        assert self.fproxy(1) == 1
        assert self.fproxy("abc") == "abc"

    def it_lookup_to_function_attributes(self):
        assert self.fproxy.someatt == 1
