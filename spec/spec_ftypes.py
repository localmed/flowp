import mock
from flowp import ftypes
from flowp.testing import Behavior
import types


################# CORE #################

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
        class TestException(Exception):
            pass

        def func():
            raise TestException()

        def func2():
            pass

        func.should = ftypes.Should(func) 
        func.should.throw(TestException).by_call()

        with self.assertRaisesRegexp(AssertionError, r'^TestException'):
            func2.should = ftypes.Should(func2)
            func2.should.throw(TestException).by_call()


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
        class SomeClass(object):
            pass

        assert isinstance(ftypes.this(1), ftypes.Int)
        assert isinstance(ftypes.this(1.1), ftypes.Float)
        assert isinstance(ftypes.this("abc"), ftypes.Str)
        assert isinstance(ftypes.this(True), ftypes.BoolAdapter)
        assert isinstance(ftypes.this(None), ftypes.NoneAdapter)
        assert isinstance(ftypes.this([1, 2, 3]), ftypes.List)
        assert isinstance(ftypes.this((1, 2, 3)), ftypes.Tuple)
        assert isinstance(ftypes.this({'a': 1, 'b': 2}), ftypes.Dict)
        assert isinstance(ftypes.this({1, 2, 3}), ftypes.Set)
        assert isinstance(ftypes.this(SomeClass), ftypes.TypeAdapter)

    def it_transform_function_types_to_flowp_function_types(self):
        class SomeClass(object):
            def method(self):
                return 1

        def function():
            return 2

        obj = SomeClass()
        assert isinstance(ftypes.this(function), ftypes.FunctionAdapter)
        assert isinstance(ftypes.this(obj.method), ftypes.FunctionAdapter)
        assert isinstance(ftypes.this("abc".index), ftypes.FunctionAdapter)

    def it_return_object_adapter_if_not_builtin_type(self):
        class SomeClass(object):
            pass

        obj = SomeClass()
        obj.a = 111
        new_obj = ftypes.this(obj)
        assert new_obj.__class__ is ftypes.ObjectAdapter
        assert new_obj._adaptee is obj
        assert new_obj.a == 111

    def it_not_transform_if_its_already_ftype(self):
        Str_mock = mock.MagicMock()
        obj = ftypes.Str('abc')
        with mock.patch.dict('flowp.ftypes.TYPES_MAP', {str:Str_mock}):
            ftypes.this(obj)
        assert not Str_mock.called

    def it_leaves_class_and_object_attributes(self):
        class SomeClass(object):
            a = 1
            
            def __init__(self):
                self.b = 2

        obj = SomeClass()
        new_obj = ftypes.this(obj)
        assert new_obj.a == 1
        assert new_obj.b == 2


############### ADAPTERS ###############

class ObjectAdapter(Behavior):
    def before_each(self):
        self.adaptee = "abc"
        self.adapter = ftypes.ObjectAdapter(self.adaptee)
    
    def class_attributes(self, klass, att_type):
        def _(att_name):
            att = getattr(klass, att_name)
            if not att_name.startswith('_') and isinstance(att, att_type):
                return True
            return False
        return filter(_, klass.__dict__.keys())

    def it_inherits_from_flowp_core_Object(self):
        assert issubclass(ftypes.ObjectAdapter, ftypes.Object)

    def it_stores_adaptee_object(self):
        assert self.adapter._adaptee is self.adaptee

    def it_pass_attribute_lookup_to_adaptee_attributes(self):
        assert self.adapter.index("c") == 2

    def it_pass_property_lookup_to_adaptee(self):
        class SomeClass(object):
            @property
            def prop(self):
                return 1

        obj = ftypes.ObjectAdapter(SomeClass())
        assert obj.prop == 1

    def it_execute_adapter_methods_with_adaptee_context(self):
        assert self.adapter.is_instanceof(str)
        assert self.adapter.hasattr('upper')
        assert self.adapter.getattr('upper')

    def it_execute_adapter_properties_with_adaptee_context(self):
        def func():
            pass
        adapter = ftypes.ObjectAdapter(func)

        assert adapter.is_instanceof(types.FunctionType)
        assert adapter.is_callable
        assert not self.adapter.is_callable
        assert self.adapter.type is str

    def it_have_Should_object_with_adaptee_context(self):
        assert self.adapter.should.context is self.adaptee

    def it_show_adapter_and_adaptee_attributes_by_dir_func(self):
        base_atts = [a for a in dir(self.adaptee) if not a.startswith('__')]
        adpt_atts = type(self.adapter).__dict__.keys()
        adpt_atts.extend(self.adapter.__dict__.keys()) 
        adpt_atts.extend(object.__dict__.keys())
        atts = list(set(base_atts + adpt_atts))
        assert set(dir(self.adapter)) == set(atts)

    def it_have_adaptee_string_representation(self):
        assert self.adapter.__repr__() == self.adaptee.__repr__()

    def it_overrides_all_properties_and_methods_from_flowp_Object(self):
        base_atts = self.class_attributes(ftypes.Object, 
                types.UnboundMethodType) \
            + self.class_attributes(ftypes.Object, property)
        adpt_atts = self.class_attributes(ftypes.ObjectAdapter, 
                types.UnboundMethodType) \
            + self.class_attributes(ftypes.ObjectAdapter, property)
        assert set(adpt_atts) >= set(base_atts)


class BoolAdapter(Behavior):
    def before_each(self):
        self.T = ftypes.BoolAdapter(True)
        self.F = ftypes.BoolAdapter(False)

    def it_simulate_conditional_checking(self):
        if not self.T:
            raise AssertionError 

        if self.F:
            raise AssertionError


class FunctionAdapter(Behavior):
    def before_each(self):
        def func(x):
            return x

        func.someatt = 1
        self.fproxy = ftypes.FunctionAdapter(func)

    def it_is_callable(self):
        assert self.fproxy(1) == 1
        assert self.fproxy("abc") == "abc"

    def it_lookup_to_function_attributes(self):
        assert self.fproxy.someatt == 1


############## CONVERTERS ##############

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


############## INTEGRATION #############

class FtypesIntegration(Behavior):
    def before_each(self):
        self.s = 'abc-def-ghi'
        self.l = ['a', 'b', 'c', 'd', 'e']
        self.nl = [1, 2, [3, 4], 5]

    def it_invokes_types_method_through_this_wrapper(self):
        assert ftypes.this(self.s).is_instanceof(ftypes.Str)
        assert ftypes.this(self.l).hasattr('index')

    def it_do_methods_chain_operations(self):
        s = ftypes.Str(self.s)
        l = ftypes.List(self.l)
        nl = ftypes.List(self.nl)
        l2 = ftypes.List(['1', '2', '1', '1', '3', '2', '4'])

        assert s.split('-').reversed.join('.') == 'ghi.def.abc'
        assert l.filter(lambda x: x != 'c') == ['a', 'b', 'd', 'e']
        assert l2.set.map(lambda x: x.int) == ftypes.Set([1, 2, 3, 4])
        assert nl.flatten.max.str == '5'