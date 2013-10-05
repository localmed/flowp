from flowp.testing import Behavior, when, expect
from flowp import testing
from unittest import mock


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

    def it_do_mock_expectations(self):
        m = mock.Mock() 
        expect(m).not_called
        with self.assertRaises(AssertionError):
            expect(m).called
        m()
        expect(m).called
        with self.assertRaises(AssertionError):
            expect(m).not_called

        m = mock.Mock()
        with self.assertRaises(AssertionError):
            expect(m).called_with(1,2,3)
        m(3,4)
        with self.assertRaises(AssertionError):
            expect(m).called_with(1,2,3)
        m(1,2,3)
        expect(m).called_with(1,2,3)


class WhenFunc(Behavior):
    def have_generator_context(self):
        self.cat = True
        yield
        self.dog = True

    def have_simple_context(self):
        self.bird = True

    def have_context_with_annotation(self) -> 'annotation context':
        pass

    @when(have_generator_context)
    def it_pass_data_from_generator_context_method(self):
        assert self.cat

    @when(have_simple_context)
    def it_pass_data_from_simple_context_method(self):
        assert self.bird

    @when(have_generator_context, have_simple_context)
    def it_pass_data_from_multi_context_methods(self):
        assert self.cat
        assert self.bird

    def it_do_setup_and_teardown_from_generator_context(self):
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

    def it_set_contexts_names_list_as_an_attribute_to_test_method_(self):
        def test_method(s):
            pass
        assert not hasattr(test_method, 'contexts')
        test_method = \
            when(self.have_generator_context, self.have_simple_context)(test_method)
        assert test_method.contexts == ['have generator context', 
            'have simple context']
        test_method = when('context1', 'context2')(test_method)
        assert test_method.contexts == ['context1', 'context2']

    def it_set_context_name_from_annotation_of_context_method_if_given(self):
        def test_method(s):
            pass

        test_method = \
            when(self.have_simple_context, self.have_context_with_annotation)(test_method)
        expect(test_method.contexts) == ['have simple context', 
            'annotation context']

    def it_executes_method_with_text_context(self):
        def test_method(s):
            raise AssertionError()

        with self.assertRaises(AssertionError):
            test_method = when('text context')(test_method) 
            test_method(self)
    
    def it_works_with_mock_decorators(self):
        def test_method(s, mock):
            raise AssertionError()

        with self.assertRaises(AssertionError):
            test_method = when('text context')(mock.patch('sys.argv')(test_method))
            test_method(self)


class ContextsTree(Behavior):
    def before_each(self):
        class Method:
            def __init__(self, name, contexts = None):
                if contexts:
                    self.contexts = contexts
                self.name = name
            
            def __repr__(self):
                return self.name

        class TestCase:
            def __init__(self, name, contexts = None):
                self._test_method = Method(name, contexts)

        self.m1 = TestCase('m1', ['ctx1'])
        self.m2 = TestCase('m2')
        self.m3 = TestCase('m3', ['ctx1', 'ctx2'])
        self.m4 = TestCase('m4', ['ctx2'])
        self.m5 = TestCase('m5', ['ctx1'])
        self.m6 = TestCase('m6', ['ctx1', 'ctx2'])
        self.tree = testing.ContextsTree([self.m1, self.m2, self.m3, self.m4,
            self.m5, self.m6])

    def it_needs_test_methods_list_as_input(self):
        pass

    def it_return_sorted_by_contexts_list_of_test_methods(self):
        expect(self.tree.list) == [self.m2, self.m1, self.m5, self.m3, 
            self.m6, self.m4] 

    def it_build_tree_by_contexts_groups(self):
        expect(self.tree.structure) == {
            None: [self.m2],
            'ctx1': {
                None: [self.m1, self.m5],
                'ctx2': {None: [self.m3, self.m6]}
            },
            'ctx2': {
                None: [self.m4]
            }
        }


class TextTestResults(Behavior):
    COLOR_GREEN = testing.TextTestResult.COLOR_GREEN
    COLOR_END = testing.TextTestResult.COLOR_END
    COLOR_RED = testing.TextTestResult.COLOR_RED
    
    def executes_startTest_and_addSuccess(self) -> 'executes .startTest and .addSuccess':
        class Method:
            def __init__(self, name, contexts = None):
                if contexts:
                    self.contexts = contexts
                self.name = name
            
            def __repr__(self):
                return self.name

        class TestCase:
            def __init__(self, name, testcase_name, contexts = None):
                self._test_method = Method(name, contexts)
                self._testcase_name = testcase_name

            def __repr__(self):
                return self._test_method.name + ' (%s)' % self._testcase_name

        class Stream:
            def __init__(self):
                self.data = ''

            def write(self, data):
                self.data += data 

            def writeln(self, data=''):
                self.write(data + "\n")

            def flush(self):
                pass

        # representation of TestCases for single test method
        self.m1 = TestCase('it_m1', 'tc1', ['ctx1'])
        self.m2 = TestCase('it_m2', 'tc1')
        self.m3 = TestCase('it_m3', 'tc1', ['ctx1', 'ctx2'])
        self.m4 = TestCase('it_m4', 'tc1', ['ctx2'])
        self.m5 = TestCase('it_m5', 'tc1', ['ctx1'])
        self.m6 = TestCase('it_m6', 'tc1', ['ctx1', 'ctx2'])
        self.m7 = TestCase('it_m7', 'tc1')
        self.m8 = TestCase('it_m8', 'tc2')
        self.results = testing.TextTestResult(Stream(), None, 2)

    @when(executes_startTest_and_addSuccess)
    def it_write_test_names_as_representation_of_single_tests(self):
        expect(self.results.stream.data) == ''
        self.results.startTest(self.m2)
        self.results.addSuccess(self.m2)
        self.results.startTest(self.m7)
        self.results.addSuccess(self.m7)
        s = "\n\ntc1:\n{green}    - m2 ... OK\n{end}{green}    - m7 ... OK\n{end}"
        expect(self.results.stream.data) == s.format(
            green=self.COLOR_GREEN,
            end=self.COLOR_END
        )

    @when(executes_startTest_and_addSuccess)
    def it_write_test_case_names_as_main_groups(self):
        expect(self.results.stream.data) == ''
        self.results.startTest(self.m2)
        self.results.addSuccess(self.m2)
        self.results.startTest(self.m7)
        self.results.addSuccess(self.m7)
        self.results.startTest(self.m8)
        self.results.addSuccess(self.m8)
        s = "\n\ntc1:\n{green}    - m2 ... OK\n{end}{green}    - m7 ... OK\n{end}"
        s += "\n\ntc2:\n{green}    - m8 ... OK\n{end}"
        expect(self.results.stream.data) == s.format(
            green=self.COLOR_GREEN,
            end=self.COLOR_END
        )

    @when(executes_startTest_and_addSuccess)
    def it_write_test_context_names_as_test_case_subgroups(self):
        expect(self.results.stream.data) == ''
        # without context
        self.results.startTest(self.m2)
        self.results.addSuccess(self.m2)
        self.results.startTest(self.m7)
        self.results.addSuccess(self.m7)
        # only ctx1 context
        self.results.startTest(self.m1)
        self.results.addSuccess(self.m1)
        self.results.startTest(self.m5)
        self.results.addSuccess(self.m5)
        # ctx1 and ctx2 context
        self.results.startTest(self.m3)
        self.results.addSuccess(self.m3)
        self.results.startTest(self.m6)
        self.results.addSuccess(self.m6)
        # only ctx2 context
        self.results.startTest(self.m4)
        self.results.addSuccess(self.m4)

        s = "\n\ntc1:\n"
        s += "{green}    - m2 ... OK\n{end}"
        s += "{green}    - m7 ... OK\n{end}"
        s += "\n"
        s += "    when ctx1:\n"
        s += "   {green}    - m1 ... OK\n{end}"
        s += "   {green}    - m5 ... OK\n{end}"
        s += "\n"
        s += "        when ctx2:\n"
        s += "      {green}    - m3 ... OK\n{end}"
        s += "      {green}    - m6 ... OK\n{end}"
        s += "\n"
        s += "    when ctx2:\n"
        s += "   {green}    - m4 ... OK\n{end}"

        expect(self.results.stream.data) == s.format(
            green=self.COLOR_GREEN,
            end=self.COLOR_END
        )

    @when(executes_startTest_and_addSuccess)
    def it_handle_module_import_error(self):
        class ModuleImportFailure:
            def __repr__(self):
                return "spec.spec_testing (TestCaseName)"

        error_test = ModuleImportFailure()
        self.results.startTest(error_test)
        # simulating addError method
        self.results.stream.write(self.COLOR_RED)
        self.results.stream.write(self.results._formatted_description(error_test))
        self.results.stream.writeln("ERROR")
        self.results.stream.write(self.COLOR_END)
        #
        self.results.printErrorList('ERROR', [(error_test, '')])

        s = "\n\nTestCaseName:\n"
        s += "{red}    - spec.spec_testing ... ERROR\n{end}"
        s += "-" * 70 + "\n\n"
        s += "{red}ERROR: \"spec.spec_testing\" [TestCaseName]\n{end}\n\n"
        
#        s = s.replace("\n", '[N]')
        self.results.stream.data = \
            self.results.stream.data.replace(self.COLOR_RED, '[R]')
        self.results.stream.data = \
            self.results.stream.data.replace(self.COLOR_END, '[E]')
#        self.results.stream.data = \
#            self.results.stream.data.replace("\n", '[N]')

        expect(self.results.stream.data) == s.format(
            red='[R]',
            end='[E]'
        )
