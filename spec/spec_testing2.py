from flowp.testing2 import Behavior, expect


class TestoMethod(Behavior):
    def test_method(self):
        print('executed')
        assert False
        pass

    def test_method2(self):
        print('executed2')

    def it_test_method3(self):
        expect(False).ok
        print('executed3')

    def it_do_something_else(self):
        expect(True).ok

    class WhenSomethingGiven(Behavior):
        def it_do_blabla(self):
            expect(True).ok
