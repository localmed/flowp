import unittest
from flowp import ftypes


class Behavior:
    pass

class expect:
    pass

def when(*args):
    pass


class Ftypes(Behavior):
    def before_each(self):
        self.s = 'abc-def-ghi'
        self.l = ['a', 'b', 'c', 'd', 'e']
        self.nl = [1, 2, [3, 4], 5, [1, 2], 3]

        self.fs = ftypes.Str(self.s)
        self.fl = ftypes.List(self.l)
        self.fnl = ftypes.List(self.nl)
        self.fl2 = ftypes.List(['1', '2', '1', '1', '3', '2', '4'])

    def it_invokes_types_method_through_this_wrapper(self):
        expect(ftypes.this(self.s)).isinstance(ftypes.Str)
        expect(ftypes.this(self.l).hasattr('index'))

    def it_do_methods_chain_operations(self):
        expect(self.fs.split('-').reversed.join('.')) == 'ghi.def.abc'
        expect(self.fl.filter(lambda x: x != 'c')) == ['a', 'b', 'd', 'e']
        expect(self.fl2.set.map(lambda x: x.int)) == ftypes.Set([1, 2, 3, 4])

    @unittest.skip("Under development")
    def it_do_methods_chain_operation_on_builtin_types_methods(self):
        expect(self.fnl.flatten.uniq.count(1).str) == '1'
        expect(self.fs.replace('b', 'z')).isinstance(ftypes.Str)
        expect(self.fs.hasattr('rfind')).isinstance(ftypes.BoolAdapter)
