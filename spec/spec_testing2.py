from flowp.testing2 import Behavior, expect


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
