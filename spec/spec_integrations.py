from flowp import ftypes
from flowp.testing import Behavior


class Ftypes(Behavior):
    def before_each(self):
        self.s = 'abc-def-ghi'
        self.l = ['a', 'b', 'c', 'd', 'e']
        self.nl = [1, 2, [3, 4], 5, [1, 2], 3]

    def it_invokes_types_method_through_this_wrapper(self):
        assert ftypes.this(self.s).isinstance(ftypes.Str)
        assert ftypes.this(self.l).hasattr('index')

    def it_do_methods_chain_operations(self):
        s = ftypes.Str(self.s)
        l = ftypes.List(self.l)
        nl = ftypes.List(self.nl)
        l2 = ftypes.List(['1', '2', '1', '1', '3', '2', '4'])

        assert s.split('-').reversed.join('.') == 'ghi.def.abc'
        assert l.filter(lambda x: x != 'c') == ['a', 'b', 'd', 'e']
        assert l2.set.map(lambda x: x.int) == ftypes.Set([1, 2, 3, 4])
