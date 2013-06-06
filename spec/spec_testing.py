from flowp.testing import Behavior, when, expect


class Expect(Behavior):
    def before_each(self):
        class Object:
            x = 1

        self.Object = Object
        self.obj = Object()

    def it_do_true_false_asserts(self):
        expect(True).ok
        expect(False).not_ok
        expect(None).not_ok
        expect('abc').ok
        expect(self.obj).ok

        with self.assertRaises(AssertionError):
            expect(False).ok
        with self.assertRaises(AssertionError):
            expect(True).not_ok


    def it_do_equality_asserts(self):
        expect(1) == 1
        expect('abc') == 'abc'
        expect(2) != 3
        expect('abc') != 'abk'
        expect(1) < 2
        expect(1) <= 1
        expect(1) > 0
        expect(2) >= 1
         
        with self.assertRaises(AssertionError):
            expect(1) == 2
        with self.assertRaises(AssertionError):
            expect('abc') != 'abc'
        with self.assertRaises(AssertionError):
            expect(2) < 2
        with self.assertRaises(AssertionError):
            expect(3) <= 2
        with self.assertRaises(AssertionError):
            expect(1) > 2
        with self.assertRaises(AssertionError):
            expect(0) >= 2

    def it_do_other_kind_of_asserts(self):
        expect(1).isinstance(int)
        expect(1).not_isinstance(str)
        expect(2).be_in([1,2,3])
        expect(4).not_be_in([1,2,3])
        expect(self.obj).be(self.obj)
        expect(self.obj).not_be(self.Object())

        with self.assertRaises(AssertionError):
            expect(1).isinstance(str)
        with self.assertRaises(AssertionError):
            expect(1).not_isinstance(int)
        with self.assertRaises(AssertionError):
            expect(4).be_in([1,2,3])
        with self.assertRaises(AssertionError):
            expect(2).not_be_in([1,2,3])
        with self.assertRaises(AssertionError):
            expect(self.obj).be(self.Object())
        with self.assertRaises(AssertionError):
            expect(self.obj).not_be(self.obj)


    def it_do_to_raise_expectation(self):
        class TestException(Exception):
            pass

        class TestException2(Exception):
            pass

        def func():
            raise TestException()

        def func2():
            pass

        expect(func).to_raise(TestException).by_call()

        with self.assertRaises(AssertionError):
            expect(func2).to_raise(TestException).by_call()


class WhenFunc(Behavior):
    def have_yield_context(self):
        self.cat = True
        yield
        self.dog = True

    def have_simple_context(self):
        self.bird = True

    @when(have_yield_context)
    def it_pass_data_from_yield_context_method(self):
        assert self.cat

    @when(have_simple_context)
    def it_pass_data_from_simple_context_method(self):
        assert self.bird

    @when(have_yield_context, have_simple_context)
    def it_pass_data_from_multi_context_methods(self):
        assert self.cat
        assert self.bird

    def it_do_setup_and_teardown_from_yield_context(self):
        def test_method(s):
            assert s.cat
            assert not hasattr(s, 'dog')

        def have_yield_context(s):
            s.cat = True
            yield
            s.dog = True

        assert not hasattr(self, 'cat')
        assert not hasattr(self, 'dog')
        test_method = when(have_yield_context)(test_method) 
        test_method(self)
        assert self.cat
        assert self.dog

    def it_set_contexts_list_to_test_method(self):
        def test_method(s):
            pass
        assert not hasattr(test_method, 'contexts')
        test_method = \
            when(self.have_yield_context, self.have_simple_context)(test_method)
        assert test_method.contexts == ['have yield context', 
            'have simple context']
        test_method = when('context1', 'context2')(test_method)
        assert test_method.contexts == ['context1', 'context2']
