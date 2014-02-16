from flowp.testing2 import Behavior, expect
from unittest import mock
import flowp.testing2.dummy


class Expect(Behavior):
    class ToBeMethod(Behavior):
        def it_should_do_true_assets(self):
            expect(True).to_be(True)
            expect([1]).to_be(True)
            with expect.to_raise(AssertionError):
                expect(False).to_be(True)
            with expect.to_raise(AssertionError):
                expect([]).to_be(True)

        def it_should_do_false_asserts(self):
            expect(False).to_be(False)
            expect([]).to_be(False)
            with expect.to_raise(AssertionError):
                expect(True).to_be(False)
            with expect.to_raise(AssertionError):
                expect([1]).to_be(False)

        def it_should_do_is_asserts(self):
            a = object()
            b = object()
            expect(a).to_be(a)
            with expect.to_raise(AssertionError):
                expect(a).to_be(b)
                
    class NotToBeMethod(Behavior):
        def it_should_do_not_true_assets(self):
            expect(False).not_to_be(True)
            expect([]).not_to_be(True)
            with expect.to_raise(AssertionError):
                expect(True).not_to_be(True)
            with expect.to_raise(AssertionError):
                expect([1]).not_to_be(True)

        def it_should_do_not_false_asserts(self):
            expect(True).not_to_be(False)
            expect([1]).not_to_be(False)
            with expect.to_raise(AssertionError):
                expect(False).not_to_be(False)
            with expect.to_raise(AssertionError):
                expect([]).not_to_be(False)

        def it_should_do_is_asserts(self):
            a = object()
            b = object()
            expect(a).not_to_be(b)
            with expect.to_raise(AssertionError):
                expect(a).not_to_be(a)

    class ToRaiseMethod(Behavior):
        def before_each(self):
            class CustomException(Exception):
                pass
            self.CustomException = CustomException

        def it_should_catch_expected_exceptions(self):
            with expect.to_raise(AssertionError):
                raise AssertionError()
            with expect.to_raise(self.CustomException):
                raise self.CustomException()

        def it_should_raise_exception_if_none_exceptions_raised(self):
            cought = False
            try:
                with expect.to_raise(AssertionError):
                    pass
            except AssertionError:
                cought = True
            expect(cought).to_be(True)

        def it_should_raise_exception_if_different_exception_raised(self):
            cought = False
            try:
                with expect.to_raise(self.CustomException):
                    raise AssertionError()
            except AssertionError:
                cought = True
            expect(cought).to_be(True)

    def it_should_do_equality_asserts(self):
        expect(1) == 1
        expect(1) != 2
        expect(2) < 3
        expect(3) > 2
        expect(2) <= 2
        expect(3) >= 2

        with expect.to_raise(AssertionError):
            expect(1) == 2
        with expect.to_raise(AssertionError):
            expect(2) != 2
        with expect.to_raise(AssertionError):
            expect(3) < 2
        with expect.to_raise(AssertionError):
            expect(2) > 3
        with expect.to_raise(AssertionError):
            expect(3) <= 2
        with expect.to_raise(AssertionError):
            expect(2) >= 3

    def it_should_do_instance_of_asserts(self):
        class Test:
            pass
        obj = Test()
        expect(1).to_be_instance_of(int)
        expect(obj).to_be_instance_of(Test)

        with expect.to_raise(AssertionError):
            expect(1).to_be_instance_of(str)
        with expect.to_raise(AssertionError):
            expect(obj).to_be_instance_of(int)
            
    def it_should_do_not_instance_of_asserts(self):
        class Test:
            pass
        obj = Test()
        expect(1).not_to_be_instance_of(str)
        expect(obj).not_to_be_instance_of(int)

        with expect.to_raise(AssertionError):
            expect(1).not_to_be_instance_of(int)
        with expect.to_raise(AssertionError):
            expect(obj).not_to_be_instance_of(Test)

    def it_should_do_in_asserts(self):
        expect(1).to_be_in([1, 2, 3])
        with expect.to_raise(AssertionError):
            expect(4).to_be_in([1, 2, 3])

    def it_should_do_not_in_asserts(self):
        expect(4).not_to_be_in([1, 2, 3])
        with expect.to_raise(AssertionError):
            expect(1).not_to_be_in([1, 2, 3])

    class MockExpectations(Behavior):
        def before_each(self):
            self.m = mock.Mock()

        def it_should_do_called_assert(self):
            self.m()
            expect(self.m).to_have_been_called()
            self.m.reset_mock()
            with expect.to_raise(AssertionError):
                expect(self.m).to_have_been_called()

        def it_should_do_not_called_assert(self):
            expect(self.m).not_to_have_been_called()
            self.m()
            with expect.to_raise(AssertionError):
                expect(self.m).not_to_have_been_called()

        def it_should_do_called_with_assert(self):
            self.m(1, 2, 3)
            expect(self.m).to_have_been_called_with(1, 2, 3)
            with expect.to_raise(AssertionError):
                expect(self.m).to_have_been_called_with(0, 2, 3)

        def it_should_do_called_n_times_assert(self):
            self.m()
            self.m()
            expect(self.m).to_have_been_called(2)
            with expect.to_raise(AssertionError):
                expect(self.m).to_have_been_called(1)


class BehaviorInstance(Behavior):
    class MockMethod(Behavior):
        class WhenTargetNotGiven(Behavior):
            def it_creates_mocks(self):
                m = self.mock()
                expect(m).to_be_instance_of(mock.Mock)

            def it_creates_mocks_with_attributes_specification(self):
                m = self.mock(spec=['a'])
                m.a
                with expect.to_raise(AttributeError):
                    m.b

        class WhenTargetGiven(Behavior):
            def it_patch_concrete_places(self):
                expect(flowp.testing2.dummy.test_var) == 0
                m = self.mock('flowp.testing2.dummy.test_var')
                expect(flowp.testing2.dummy.test_var)\
                    .to_be_instance_of(mock.Mock)
                expect(m).to_be(flowp.testing2.dummy.test_var)

            def it_patch_with_new_parameter(self):
                expect(flowp.testing2.dummy.test_var) == 0
                self.mock('flowp.testing2.dummy.test_var', new=1)
                expect(flowp.testing2.dummy.test_var) == 1

            def it_patch_with_attributes_specification(self):
                expect(flowp.testing2.dummy.test_var) == 0
                m = self.mock('flowp.testing2.dummy.test_var', spec=['a'])
                flowp.testing2.dummy.test_var.a
                with expect.to_raise(AttributeError):
                    flowp.testing2.dummy.test_var.b

        class WhenTargetAndAttrGiven(Behavior):
            def before_each(self):
                class Object:
                    pass
                self.o = Object()
                self.o.a = 0

            def it_patch_object_attributes(self):
                m = self.mock(self.o, 'a')
                expect(self.o.a).to_be_instance_of(mock.Mock)
                expect(m).to_be(self.o.a)

            def it_patch_with_new_parameter(self):
                self.mock(self.o, 'a', new=1)
                expect(self.o.a) == 1

            def it_patch_with_attributes_specification(self):
                expect(flowp.testing2.dummy.test_var) == 0
                self.mock(self.o, 'a', spec=['a'])
                self.o.a
                with expect.to_raise(AttributeError):
                    self.o.a.c

    class RunMethod(Behavior):
        def it_removes_mocks_patchers_after_each_test_method0(self):
            expect(flowp.testing2.dummy.test_var) == 0
            expect(flowp.testing2.dummy.test_obj.a) == 0
            self.mock('flowp.testing2.dummy.test_var', new=1)
            self.mock(flowp.testing2.dummy.test_obj, 'a', new=1)
            expect(flowp.testing2.dummy.test_var) == 1
            expect(flowp.testing2.dummy.test_obj.a) == 1

        def it_removes_mocks_patchers_after_each_test_method(self):
            expect(flowp.testing2.dummy.test_var) == 0
            expect(flowp.testing2.dummy.test_obj.a) == 0
            self.mock('flowp.testing2.dummy.test_var', new=1)
            self.mock(flowp.testing2.dummy.test_obj, 'a', new=1)
            expect(flowp.testing2.dummy.test_var) == 1
            expect(flowp.testing2.dummy.test_obj.a) == 1
