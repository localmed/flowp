import functools
import types


class ShouldThrow(object):
    def __init__(self, should_obj):
        self.should_obj = should_obj
        self.exception_class = None

    def __call__(self, expected_exception_class):
        self.expected_exception_class = expected_exception_class
        return self

    def by_call(self, *args, **kwargs):
        try:
            self.should_obj.context(*args, **kwargs)
            assert False, "%s exception should be raised" % \
                self.expected_exception_class
        except self.expected_exception_class:
            pass 


class Should(object):
    Throw = ShouldThrow

    def __init__(self, context):
        """
        Construct Should object
        @param context: context of Should object
        """
        self.context = context
        self.throw = self.Throw(self)

    def __eq__(self, other):
        assert self.context == other

    def __ne__(self, other):
        assert self.context != other

    def __lt__(self, other):
        assert self.context < other

    def __le__(self, other):
        assert self.context <= other

    def __gt__(self, other):
        assert self.context > other

    def __ge__(self, other):
        assert self.context >= other

    def be(self, other):
        assert self.context is other

    def not_be(self, other):
        assert self.context is not other

    @property
    def be_true(self):
        assert self.context.subject is True
        return None

    @property
    def be_false(self):
        assert self.context.subject is False
        return None

    @property
    def be_none(self):
        assert self.context.value is None

    def be_in(self, other):
        assert self.context in other

    def not_be_in(self, other):
        assert self.context not in other

    def be_instanceof(self, other):
        assert isinstance(self.context, other) is True

    def not_be_instanceof(self, other):
        assert isinstance(self.context, other) is False


class Object(object):
    Should = Should

    @property
    def should(self):
        if not hasattr(self, '_should'):
            self._should = self.Should(self)
        return self._should

    @property
    def type(self):
        return type(self)

    @property
    def is_callable(self):
        return callable(self)

    def is_instanceof(self, klass):
        return isinstance(self, klass)

    def hasattr(self, name):
        return hasattr(self, name)

    def getattr(self, name):
        return getattr(self, name)


class Iterable(Object):
    @property
    def len(self):
        return len(self)

    @property
    def all(self):
        return all(self)

    @property
    def any(self):
        return any(self)

    @property
    def min(self):
        return min(self)

    @property
    def max(self):
        return max(self)

    @property
    def sum(self):
        return sum(self)

    def map(self, func):
        return map(func, self)

    def filter(self, func):
        return filter(func, self)

    def reduce(self, func):
        return functools.reduce(func, self)


class List(list, Iterable):
    pass


class Tuple(tuple, Iterable):
    pass


class Set(set, Iterable):
    pass


class Frozenset(frozenset, Iterable):
    pass


class Bytes(bytes, Iterable):
    pass


class Bytearray(bytearray, Iterable):
    pass


class Str(str, Iterable):
    @property
    def int(self):
        return Int(self)


class Int(int, Object):
    @property
    def str(self):
        return Str(self)


class Float(float, Object):
    pass


class Complex(complex, Object):
    pass


class Dict(dict):
    pass


class TypesPropagator(object):
    def __getattribute__(self, item):
        return this(object.__getattribute__(self, item))


class ObjectProxy(object):
    def __init__(self, subject):
        self.subject = subject

    def __getattr__(self, item):
        return getattr(self.subject, item)


class BoolProxy(ObjectProxy):
    def __bool__(self):
        return self.subject


class NoneProxy(ObjectProxy):
    pass


class FunctionProxy(ObjectProxy):
    def __call__(self, *args, **kwargs):
        return self.subject(*args, **kwargs)


def this(obj):
    types_map = {
        int: Int,
        float: Float,
        str: Str,
        bool: BoolProxy,
        type(None): NoneProxy,
        list: List,
        tuple: Tuple,
        dict: Dict,
        set: Set,
        types.MethodType: FunctionProxy,
        types.BuiltinMethodType: FunctionProxy,
        types.FunctionType: FunctionProxy,
        types.BuiltinFunctionType: FunctionProxy,
        types.LambdaType: FunctionProxy,
    }

    obj_type = type(obj)
    if obj_type in types_map.keys():
        new_type = types_map[obj_type]
        return new_type(obj)

    # if not built-in type, inject Object class inheritance to object copy
    obj_class_name = obj_type.__name__
    newclass = type(obj_class_name, (obj_type, Object), dict())
    obj.__class__ = newclass
    return obj
