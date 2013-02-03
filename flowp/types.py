import functools

class List(list):
    # Types transformation properties
    @property
    def set(self):
        return Set(self)

    @property
    def tuple(self):
        return Tuple(self)

    @property
    def str(self):
        return Str(self)

    # Function operation properties
    @property
    def min(self):
        return min(self)

    @property
    def max(self):
        return max(self)

    @property
    def len(self):
        return Int(len(self))

    @property
    def sum(self):
        return sum(self)

    # Function operation methods
    def map(self, func):
        return List(map(func, self))

    def filter(self, func):
        return List(filter(func, self))

    def reduce(self, func):
        return List(functools.reduce(func, self))

class Tuple(tuple):
    pass

class Set(set):
    pass

class Str(str):
    @property
    def int(self):
        return Int(self)

class Int(int):
    @property
    def str(self):
        return Str(self)
