# Module have name typess not types because of annoying PyCharm TestRunner bug
# http://youtrack.jetbrains.com/issue/PY-8697

from flowp import testing
from flowp import types

class ListTest(testing.TestCase):
    def setUp(self):
        self.l = self.subject(types.List([1,2,3]))

    def test_type_transformation_properties(self):
        self.l.tuple.should == types.Tuple((1,2,3))
        self.l.set.should == types.Set([1,2,3])
        self.l.str.should == types.Str("[1, 2, 3]")

    def test_function_like_operator_properties(self):
        self.l.min.should == types.Int(1)
        self.l.max.should == types.Int(3)
        l2 = self.subject(types.List([True, False, True]))
        l3 = self.subject(types.List([True, True, True]))
        l4 = self.subject(types.List([False, False, False]))
#       l2.all.should.be_false
#       l3.all.should.be_true
#       l2.any.should.be_true
#       l4.any.should.be_false
        self.l.len.should == types.Int(3)
        self.l.sum.should == types.Int(6)

    def test_function_like_operator_methods(self):
        self.l.map(lambda x: x*2).should == types.List([2,4,6])
        self.l.filter(lambda x: x==2).should == types.List([1,3])
        self.l.reduce(lambda a,b: a+b).should == types.Int([6])
        lstr = types.List(['a', 'b', 'c'])
        lstr.join('-').should == types.Str("a-b-c")


class StrIntTest(testing.TestCase):
   def test_type_transformation_properties(self):
       some_int = self.subject(types.Int(3))
       some_str = self.subject(types.Str("2"))
       some_int.str.should == types.Str("3")
       some_str.int.should == types.Int(2)