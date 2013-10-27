from unittest import mock
from flowp import ftypes
from flowp.testing import Behavior, expect, when
import types


################# CORE #################

class Ftypes(Behavior):
    def it_have_object_interface(self):
        ftypes.Object.type
        ftypes.Object.iscallable
        ftypes.Object.isinstance
        ftypes.Object.hasattr
        ftypes.Object.getattr
        ftypes.Object.dir
        #ftypes.Object.clone

    def it_have_container_interface(self):
        ftypes.Container.len
        ftypes.Container.all
        ftypes.Container.any
        ftypes.Container.min
        ftypes.Container.max
        ftypes.Container.sum
        ftypes.Container.map
        ftypes.Container.map_it
        ftypes.Container.filter
        ftypes.Container.filter_it
        ftypes.Container.reduce
        ftypes.Container.join
        ftypes.Container.set
        ftypes.Container.uniq 
        ftypes.Container.flatten
        ftypes.Container.replace
        ftypes.Container.grep




class Object(Behavior):
    Subject = ftypes.Object

    def before_each(self):
        class SubjectWrapper(self.Subject):
            x = 1

        self.SubjectWrapper = SubjectWrapper

    def it_have_basic_interface(self):
        self.Subject.type
        self.Subject.iscallable
        self.Subject.isinstance
        self.Subject.hasattr
        self.Subject.getattr
        self.Subject.dir

    def it_have_type_property(self):
        expect(self.Subject().type).be(self.Subject)
        expect(self.Subject().type).not_be(object)

    def it_have_iscallable_property(self):
        class Callable(self.Subject):
            def __call__(self):
                return True

        expect(self.Subject().iscallable).not_ok
        expect(Callable().iscallable).ok

    def it_have_isinstance_method(self):
        expect(self.Subject().isinstance(self.Subject))

    def it_have_hasattr_method(self):
        expect(self.SubjectWrapper().hasattr('x')).ok
        expect(self.SubjectWrapper().hasattr('y')).not_ok

    def it_have_getattr_method(self):
        expect(self.SubjectWrapper().getattr('x')) == 1
    
    def it_have_dir_property(self):
        subject = self.SubjectWrapper()
        expect(subject.dir) == dir(subject)
        expect('x').be_in(subject.dir)


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

class Container(Behavior):
    class Tuple(tuple, ftypes.Container):
        pass

    class List(list, ftypes.Container):
        pass

    def before_each(self):
        class List(list, ftypes.Container):
            pass

        self.Subject = List
        self.subject = self.Subject([2,1,3])
        self.tuple1 = self.Tuple((1, 2, 3))
        self.tuple2 = self.Tuple((True, True, True))
        self.tuple3 = self.Tuple((True, False, True))
        self.tuple4 = self.Tuple((False, False, False))
        self.list = self.List([1,2,3])

    def it_have_len_property(self):
        expect(self.Subject([1,2,3]).len) == 3

    def it_have_all_any_property(self):
        expect(self.Subject([True, True, True]).all).ok
        expect(self.Subject([True, False, True]).all).not_ok
        expect(self.Subject([True, False]).any).ok
        expect(self.Subject([False, False]).any).not_ok

    def it_have_min_max_properties(self):
        expect(self.subject.min) == 1
        expect(self.subject.max) == 3

    def it_have_sum_property(self):
        expect(self.subject.sum) == 6

    def it_have_map_filter_reduce_methods(self):
        expect(self.subject.map(lambda x: 2*x)) == self.Subject([4,2,6])
        expect(self.subject.filter(lambda x: x in (1,3))) == self.Subject([1,3])
        expect(self.subject.reduce(lambda a,b: a*b)) == 6

    def it_have_map_filter_destructive_methods(self):
        self.subject.map_it(lambda x: x*2)
        expect(self.subject) == self.Subject([4,2,6])
        self.subject.filter_it(lambda x: x != 4)
        expect(self.subject) == self.Subject([2,6])

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
        expect(self.Subject([1,1,2,3,2,4]).uniq) == self.Subject([1,2,3,4])

    def it_do_join_operation(self):
        class Obj:
            def __repr__(self):
                return 'x'

        expect(self.Subject(['a', 'b', 'c']).join('.')) == 'a.b.c'
        expect(self.Subject(['a', 1, 'c']).join('.')) == 'a.1.c'
        expect(self.Subject(['a', Obj(), 'c']).join('.')) == 'a.x.c'
 
    def it_do_replace_operation(self):
        class Obj:
            pass
        obj = Obj()
        subject = self.Subject([1, [1,2], obj])
        
        expect(self.subject.replace(2, 4)) == self.Subject([4,1,3])
        expect(self.Subject(['a', 'b']).replace('b', 'c')) == self.Subject(['a','c'])
        expect(subject.replace([1,2], 'x')) == self.Subject([1,'x',obj])
        expect(subject.replace(obj, 3)) == self.Subject([1, [1,2], 3])

    def it_do_grep_operation(self):
        class Ob:
            pass
        c1 = self.Subject([1, 'abck', 'hbook', 31])
        c2 = self.Subject(['a', [1,2], Ob(), 'bc'])
        expect(c1.grep('b')) == self.Subject(['abck', 'hbook'])
        expect(c1.grep('^a')) == self.Subject(['abck'])
        expect(c1.grep('1')) == self.Subject([1,31])
        expect(c1.grep(1)) == self.Subject([1,31])
        expect(c2.grep([1,2])) == self.Subject([[1,2]])


class List(Behavior):
    def it_have_dict_property(self):
        assert ftypes.List([(1,2), (3,4)]).dict == {1:2, 3:4}


class Tuple(Behavior):
    def it_have_dict_property(self):
        assert ftypes.Tuple(((1,2), (3,4))).dict == {1:2, 3:4}

########### OTHER STRUCTURES ###########

class DependencyGraph(Behavior):
    def before_each(self):
        class V:
            def __init__(self, name):
                self.name = name

            def __repr__(self):
                return self.name

        self.subject = ftypes.DependencyGraph()
        self.a = V('a')
        self.b = V('b')
        self.c = V('c')
        self.d = V('d')
         
    @when('executes list')
    def it_return_sorted_dependency_sequence(self):
        self.subject[self.b] = {self.d}
        self.subject[self.a] = {self.b, self.c}
        l = self.subject.list(self.a)
        expect(l[-1]) == self.a
        expect(l.index(self.b)) > l.index(self.d)
        expect(l.len) == 4

    @when('executes list')
    def it_solves_dependency_cycle(self):
        self.subject[self.c] = {self.a} 
        self.subject[self.b] = {self.d}
        self.subject[self.a] = {self.b, self.c}
        l = self.subject.list(self.a)
        expect(l[-1]) == self.a
        expect(l.index(self.b)) > l.index(self.d)
        expect(l.len) == 4

    @when('executes list')
    def it_return_uniq_objects(self):
        self.subject[self.c] = {self.b} 
        self.subject[self.a] = {self.b, self.c}
        l = self.subject.list(self.a)
        expect(l[-1]) == self.a
        expect(l.index(self.c)) > l.index(self.b)
        expect(l.len) == 3
        
