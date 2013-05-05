from flowp.testing import Behavior, when


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
