from unittest import mock
from flowp import ftypes
from flowp.testing import Behavior
import types


################# CORE #################

class Object(Behavior):
    class SomeClass(ftypes.Object):
        x = 1

    def before_each(self):
        self.object = ftypes.Object()

    def it_have_type_property(self):
        assert self.object.type is ftypes.Object
        assert self.object.type is not object

    def it_have_iscallable_property(self):
        class Callable(ftypes.Object):
            def __call__(self):
                return True

        assert not self.object.iscallable
        assert Callable().iscallable

    def it_have_isinstance_method(self):
        assert self.object.isinstance(ftypes.Object)

    def it_have_hasattr_method(self):
        ob = self.SomeClass()
        assert ob.hasattr('x')
        assert not ob.hasattr('y')

    def it_have_getattr_method(self):
        ob = self.SomeClass()
        assert ob.getattr('x') == 1
    
    def it_have_dir_property(self):
        obj = self.SomeClass()
        assert obj.dir == dir(obj)
        assert 'x' in obj.dir


class ThisMethod(Behavior):
    def it_transforms_builtin_types_to_flowp_types(self):
        class SomeClass:
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
        class SomeClass:
            def method(self):
                return 1

        def function():
            return 2

        obj = SomeClass()
        assert isinstance(ftypes.this(function), ftypes.FunctionAdapter)
        assert isinstance(ftypes.this(obj.method), ftypes.FunctionAdapter)
        assert isinstance(ftypes.this("abc".index), ftypes.FunctionAdapter)

    def it_return_object_adapter_if_not_builtin_type(self):
        class SomeClass:
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
        assert ftypes.this(obj) is obj

    def it_leaves_class_and_object_attributes(self):
        class SomeClass:
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
        return list(filter(_, klass.__dict__.keys()))

    def it_inherits_from_flowp_core_Object(self):
        assert issubclass(ftypes.ObjectAdapter, ftypes.Object)

    def it_stores_adaptee_object(self):
        assert self.adapter._adaptee is self.adaptee

    def it_pass_attribute_lookup_to_adaptee_attributes(self):
        assert self.adapter.index("c") == 2

    def it_pass_property_lookup_to_adaptee(self):
        class SomeClass:
            @property
            def prop(self):
                return 1

        obj = ftypes.ObjectAdapter(SomeClass())
        assert obj.prop == 1

    def it_execute_adapter_methods_with_adaptee_context(self):
        assert self.adapter.isinstance(str)
        assert self.adapter.hasattr('upper')
        assert self.adapter.getattr('upper')

    def it_execute_adapter_properties_with_adaptee_context(self):
        def func():
            pass
        adapter = ftypes.ObjectAdapter(func)

        assert adapter.isinstance(types.FunctionType)
        assert adapter.iscallable
        assert not self.adapter.iscallable
        assert self.adapter.type is str

    def it_show_adapter_and_adaptee_attributes_by_dir_func(self):
        base_atts = [a for a in dir(self.adaptee) if not a.startswith('__')]
        adpt_atts = list(type(self.adapter).__dict__.keys())
        adpt_atts.extend(self.adapter.__dict__.keys()) 
        adpt_atts.extend(object.__dict__.keys())
        atts = list(set(base_atts + adpt_atts))
        assert set(dir(self.adapter)) == set(atts)

    def it_have_adaptee_string_representation(self):
        assert self.adapter.__repr__() == self.adaptee.__repr__()

    def it_overrides_all_properties_and_methods_from_flowp_Object(self):
        base_atts = self.class_attributes(ftypes.Object, 
                types.FunctionType) \
            + self.class_attributes(ftypes.Object, property)
        adpt_atts = self.class_attributes(ftypes.ObjectAdapter, 
                types.FunctionType) \
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
        self.fadapter = ftypes.FunctionAdapter(func)

    def it_is_callable(self):
        assert self.fadapter(1) == 1
        assert self.fadapter("abc") == "abc"

    def it_lookup_to_function_attributes(self):
        assert self.fadapter.someatt == 1

    def it_convert_function_arguments_to_flowp_types(self):
        def func(x, y):
            assert isinstance(x, ftypes.Str)
            assert isinstance(y, ftypes.Int)

        fadapter = ftypes.FunctionAdapter(func)
        fadapter('abc', y=3)


############## CONVERTERS ##############

class Iterable(Behavior):
    class Tuple(tuple, ftypes.Iterable):
        pass

    class List(list, ftypes.Iterable):
        pass

    def before_each(self):
        self.tuple1 = self.Tuple((1, 2, 3))
        self.tuple2 = self.Tuple((True, True, True))
        self.tuple3 = self.Tuple((True, False, True))
        self.tuple4 = self.Tuple((False, False, False))
        self.list = self.List([1,2,3])

    def it_have_len_property(self):
        assert self.tuple1.len == 3

    def it_have_all_any_property(self):
        assert self.tuple2.all
        assert not self.tuple3.all
        assert self.tuple2.any
        assert self.tuple3.any
        assert not self.tuple4.any

    def it_have_min_max_properties(self):
        assert self.tuple1.min == 1
        assert self.tuple1.max == 3

    def it_have_sum_property(self):
        assert self.tuple1.sum == 6

    def it_have_map_filter_reduce_methods(self):
        self.tuple1.map(lambda x: 2*x) == self.Tuple((2, 4, 6))
        self.tuple1.filter(lambda x: x in (1, 3)) == self.Tuple((1, 3))
        self.tuple1.reduce(lambda a, b: a*b) == 6

    def it_have_map_filter_destructive_methods(self):
        self.list.map_it(lambda x: x*2)
        assert self.list == [2,4,6] 
        self.list.filter_it(lambda x: x != 4)
        assert self.list == [2,6]

    def it_do_flatten_operation(self):
        assert self.List([[1,2],[3,4],[5,6]]).flatten == [1,2,3,4,5,6]
        assert self.List([1,[2,3],4,[5,6]]).flatten == [1,2,3,4,5,6] 
        assert self.List([1,[2,[3,4]],5,[6]]).flatten == [1,2,[3,4],5,6]
        assert self.Tuple(((1,2),(3,4),(5,6))).flatten == (1,2,3,4,5,6)
        assert self.Tuple((1,(2,3),4,(5,6))).flatten == (1,2,3,4,5,6) 
        assert self.Tuple((1,(2,(3,4)),5,(6))).flatten == (1,2,(3,4),5,6)
        # Mixed situations, lists, tuples together
        assert self.List([1,(2,3),[4,5],6,(7,8),9,[10,11]]).flatten == \
            [1,2,3,4,5,6,7,8,9,10,11]
        assert self.Tuple((1,(2,3),[4,5],6,(7,8),9,[10,11])).flatten == \
            (1,2,3,4,5,6,7,8,9,10,11)
    
    def it_do_uniq_operation(self):
        l = self.List([1,1,2,3,2,4])
        t = self.Tuple([1,1,2,3,2,4])
        assert l.uniq == [1,2,3,4]
        assert t.uniq == (1,2,3,4)

    def it_do_join_operation(self):
        class Obj:
            def __repr__(self):
                return 'x'
 
        assert self.List(['a', 'b', 'c']).join('.') == 'a.b.c'
        # it should join even not str elements
        assert self.List(['a', 1, 'c']).join('.') == 'a.1.c'
        assert self.List(['a', Obj(), 'c']).join('.') == 'a.x.c'

    def it_do_replace_operation(self):
        class Obj:
            pass
        obj = Obj()
        t = self.Tuple((1, (1,2), obj))
        assert self.tuple1.replace(2, 4) == (1,4,3)
        assert self.Tuple(('a', 'b')).replace('b', 'c') == ('a', 'c')
        assert t.replace((1,2), 'x') == (1, 'x', obj)
        assert t.replace(obj, 3) == (1, (1,2), 3)

    def it_do_grep_operation(self):
        class Ob:
            pass
        t = self.Tuple((1, 'abck', 'hbook', 31))
        t2 = self.Tuple(('a', [1,2], Ob(), 'bc'))
        assert t.grep('b') == ('abck', 'hbook')
        assert t.grep('^a') == ('abck',)
        assert t.grep('1') == (1, 31)
        assert t.grep(1) == (1, 31)
        assert t2.grep([1,2]) == ([1,2],)


class List(Behavior):
    def it_have_dict_property(self):
        assert ftypes.List([(1,2), (3,4)]).dict == {1:2, 3:4}


class Tuple(Behavior):
    def it_have_dict_property(self):
        assert ftypes.Tuple(((1,2), (3,4))).dict == {1:2, 3:4}
