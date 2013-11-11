import functools
import types
import re


################# CORE #################

def this(obj):
    """Basic type converter. Convert given object to the flowp type object 
    with type which is consistent with flowp types.
    Examples:

        class SomeClass:
            pass
        some_obj = SomeClass()

        this([1,2,3]) is ftypes.List([1,2,3])
        this(1) is ftypes.Int(1)
        this(some_obj).__class__ is ObjectAdapter
    """
    # If it's already ftype.Object, return as is
    if isinstance(obj, Object):
        return obj

    # If built-in type convert from TYPES_MAP
    obj_type = type(obj)
    if obj_type in TYPES_MAP.keys():
        new_type = TYPES_MAP[obj_type]
        return new_type(obj)

    # If not built-in type or ftype.Object, return ObjectAdapter 
    # with given obj as adaptee
    return ObjectAdapter(obj)

class Type(type):
    pass

class Object:
    @property
    def type(self):
        return type(self)

    @property
    def iscallable(self):
        return callable(self)

    def isinstance(self, klass):
        return isinstance(self, klass)

    def hasattr(self, name):
        return hasattr(self, name)

    def getattr(self, name):
        return getattr(self, name)

    @property
    def dir(self):
        return List(dir(self))


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
    def type(self):
        return type(self._adaptee)

    @property
    def iscallable(self):
        return callable(self._adaptee)

    def isinstance(self, klass):
        return isinstance(self._adaptee, klass) 

    def hasattr(self, name):
        return hasattr(self._adaptee, name)

    def getattr(self, name):
        return getattr(self._adaptee, name)

    @property
    def dir(self):
        return dir(self)


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

class Container(Object):
    """It diffs from collections.abc.Container in that it have characterictic of
    collections.abc.Container, collections.abc.Iterable and 
    collections.abc.Sized. Similar to collections.abc.Sequence, but order of 
    items is not important. It is base for List, Tuple, Str, Set. 
    """
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
        return self.type(map(FunctionAdapter(func), self))

    def map_it(self, func):
        """Like map method, but modify object itself"""
        func = FunctionAdapter(func)
        i = 0
        for item in self:
            self[i] = func(item)
            i += 1

    def filter(self, func):
        return self.type(filter(FunctionAdapter(func), self))

    def filter_it(self, func):
        """Like filter method, but modify object itself""" 
        func = FunctionAdapter(func)
        for item in self:
            if not func(item):
                self.remove(item)

    def reduce(self, func):
        return functools.reduce(FunctionAdapter(func), self)

    def join(self, glue):
        """Join elements of iterable with glue element. Even elements
        of iterable which are not string object will be joined, by
        converting.
        :param str glue:
            glue element
        """
        def func(item):
            if isinstance(item, str):
                return item
            else:
                return str(item)

        iterable = map(func, self)
        return glue.join(iterable)

    @property
    def set(self):
        return Set(self)

    @property
    def uniq(self):
        """Remove repeated elements"""
        return self.type(set(self))

    @property
    def flatten(self):
        l = []
        for item in self:
            if isinstance(item, list) or isinstance(item, tuple) \
                or isinstance(item, set):
                
                l.extend(list(item))
            else:
                l.append(item)
        return self.type(l)

    def replace(self, from_obj, to_obj):
        return self.type([to_obj if o == from_obj else o for o in self])

    def grep(self, pattern):
        if not isinstance(pattern, str):
            pattern = re.escape(str(pattern))
        
        return self.type([item for item in self if re.search(pattern, str(item))]) 


class List(list, Container):
    @property
    def reversed(self):
        lst = self[:]
        lst.reverse()
        return List(lst)

    @property
    def dict(self):
        return Dict(self)


class Tuple(tuple, Container):
    @property
    def dict(self):
        return Dict(self)


class Set(set, Container):
    def map(self, func):
        return Set(super().map(func))


class Str(str, Container):
    @property
    def int(self):
        return Int(self)

    def split(self, *args, **kwargs):
        return List(super().split(*args, **kwargs))


class Int(int, Object):
    @property
    def str(self):
        return Str(self)


class Float(float, Object):
    pass



class Dict(dict):
    pass


class DependencyGraph(Dict):
    def list(self, *vertices):
        """Do topological sorting of graph, starting from given vertices."""
        # These variables ideologically are not the same! It's important!
        # reversed(visited_vertices) != sorted_vertices -> there are cases where these
        # sequences are not the same
        visited_vertices = Set()
        sorted_vertices = List([])

        def visit(vertice):
            # Prevent from cycle
            if vertice in visited_vertices:
                return None
            else:
                visited_vertices.add(vertice)

            if vertice in self:
                for dep_vertice in self[vertice]:
                    visit(dep_vertice)
            sorted_vertices.append(vertice)

        for vertice in vertices:
            visit(vertice)
        return sorted_vertices



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

