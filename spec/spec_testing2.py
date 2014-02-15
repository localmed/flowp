from flowp import testing2


class Testo(testing2.Behavior):
    def test_method(self):
        print('executed')
        assert False
        pass

    def test_method2(self):
        print('executed2')

    def it_test_method3(self):
        assert False
        print('executed3')
