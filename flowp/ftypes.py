import functools
import types


################# CORE #################

def this(obj):
    """Convert object to the object with type which is consistent with flowp 
    types.
    Examples:

        class SomeClass(object):
            pass
        some_obj = SomeClass()

        this([1,2,3]) is ftypes.List([1,2,3])
        this(1) is ftypes.Int(1)
        this(some_obj).__class__ is ObjectAdapter
    """
    obj_type = type(obj)

    # If built-in type convert from TYPES_MAP
    if obj_type in TYPES_MAP.keys():
        new_type = TYPES_MAP[obj_type]
        return new_type(obj)

    # If not built-in type, return ObjectAdapter with given obj as adaptee
    return ObjectAdapter(obj)

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
                self.expected_exception_class.__name__
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


class Type(type):
    pass

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


############### ADAPTERS ###############

class ObjectAdapter(Object):
    def __init__(self, adaptee):
        self._adaptee = adaptee

    def __getattr__(self, name):
        return getattr(self._adaptee, name)

    def __repr__(self):
        return self._adaptee.__repr__()

    def __dir__(self):
        atts = [a for a in dir(self._adaptee) if not a.startswith('__')]
        atts.extend(self.__dict__.keys())
        atts.extend(type(self).__dict__.keys())
        atts.extend(object.__dict__.keys())
        atts = list(set(atts))
        return atts

    @property
    def should(self):
        if not hasattr(self, '_should'):
            self._should = self.Should(self._adaptee)
        return self._should

    @property
    def type(self):
        return type(self._adaptee)

    @property
    def is_callable(self):
        return callable(self._adaptee)

    def is_instanceof(self, klass):
        return isinstance(self._adaptee, klass) 

    def hasattr(self, name):
        return hasattr(self._adaptee, name)

    def getattr(self, name):
        return getattr(self._adaptee, name)


class BoolAdapter(ObjectAdapter, int):
    pass


class NoneAdapter(ObjectAdapter):
    pass


class FunctionAdapter(ObjectAdapter):
    def __call__(self, *args, **kwargs):
        args = tuple(this(a) for a in args)
        kwargs = {key: this(value) for key, value in kwargs.items()}
        return self._adaptee(*args, **kwargs)


class TypeAdapter(ObjectAdapter):
    pass


############## CONVERTERS ##############

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
        return map(FunctionAdapter(func), self)

    def filter(self, func):
        return filter(FunctionAdapter(func), self)

    def reduce(self, func):
        return functools.reduce(FunctionAdapter(func), self)

    def join(self, glue):
        return glue.join(self)

    @property
    def set(self):
        return Set(self)


class List(list, Iterable):
    @property
    def reversed(self):
        lst = self[:]
        lst.reverse()
        return List(lst)


class Tuple(tuple, Iterable):
    pass


class Set(set, Iterable):
    def map(self, func):
        return Set(super(Set, self).map(func))


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

    def split(self, *args, **kwargs):
        return List(super(Str, self).split(*args, **kwargs))


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


TYPES_MAP = {
    int: Int,
    float: Float,
    str: Str,
    bool: BoolAdapter,
    type(None): NoneAdapter,
    list: List,
    tuple: Tuple,
    dict: Dict,
    set: Set,
    type: TypeAdapter,
    types.MethodType: FunctionAdapter,
    types.BuiltinMethodType: FunctionAdapter,
    types.FunctionType: FunctionAdapter,
    types.BuiltinFunctionType: FunctionAdapter,
    types.LambdaType: FunctionAdapter,
}

