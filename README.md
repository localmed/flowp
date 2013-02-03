flowp
=====

Goal of the flowp library is to get more fun with Python. Library try to realize this on several levels.
For now flowp.testing module is available, experimental solution for BDD (Behavior Driven Development) in Python,
influenced by RSpec.

For example, with flowp.testing module You can do something like this:

```python
from flowp import testing

class Something:
    def __init__(self):
        self.a = "abc"

    def c(self):
        return 3

class SomeTest(testing.TestCase):
    def setUp(self):
        self.obj = self.subject(Something())

    def test_something(self):
        self.obj.should.be_instanceof(Something)
        self.obj.a.should == "abc"
        self.obj.c().should.be_instanceof(int)
        self.obj.c().should == 3
```

```python
self.obj.a.should == "abc"
```
is equal to

```python
self.assertEqual(self.obj.a, "abc")
```

Should expressions behave exactly like unittest.TestCase assert expressions, but they are more cleaner and handy.
