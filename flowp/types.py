from functools import reduce

class Should:
    def __init__(self, context):
        """
        Construct Should object
        @param context: context of Should object
        """
        self.context = context

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
        assert self.context is True

    @property
    def be_false(self):
        assert self.context is False

    @property
    def be_none(self):
        assert self.context is None

    def be_in(self, other):
        assert self.context in other

    def not_be_in(self, other):
        assert self.context not in other

    def be_instanceof(self, other):
        assert isinstance(self.context, other) is True

    def not_be_instanceof(self, other):
        assert isinstance(self.context, other) is False

class Object:
    pass

class Iterable(Object):
    pass

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

class TypesPropagator:
    pass

class BoolProxy:
    pass

class NoneProxy:
    pass