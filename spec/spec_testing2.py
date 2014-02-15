from flowp.testing2 import Behavior, expect


class Testo(Behavior):
    def test_method(self):
        print('executed')
        assert False
        pass

    def test_method2(self):
        print('executed2')

    def it_test_method3(self):
        expect(False).ok
        print('executed3')
