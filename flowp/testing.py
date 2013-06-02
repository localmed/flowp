import unittest
import unittest.main
import re
import contextlib
import inspect
import sys


class BDDTestCase(type):
    """Meta class for test case class (Behavior). Creates aliases 
    for setUp and tearDown methods: before_each and after_each.
    """
    def __new__(cls, name, bases, namespace):
        new_namespace = {}
        for key, value in namespace.items():
            if key == 'before_each':
                key = 'setUp'

            if key == 'after_each':
                key = 'tearDown'

            new_namespace[key] = value

        return type.__new__(cls, name, bases, new_namespace)


class Behavior(unittest.TestCase, metaclass=BDDTestCase):
    pass


def when(*context_methods):
    """Creates context for specyfic method from generator function.
    Works as decorator. Example:

        def login_as_admin(self):
            self.do_some_setup()
            yield # base instructions
            self.do_some_teardown()

        @when(login_as_admin)
        def it_act_like_a_hero(self):
            # base instructions
            pass

    Under the hood it wrap method by with statement. '@when' decorator
    can consume many contexts.

        @when(login_as_admin, have_wine)
    """
    def get_new_test_method(test_method, context_method):
        isgeneratorfunction = inspect.isgeneratorfunction(context_method)
        if isgeneratorfunction:
            context_method = contextlib.contextmanager(context_method)
        
        def new_test_method(self, *args, **kwargs):
            if isgeneratorfunction:
                with context_method(self):
                    return test_method(self, *args, **kwargs)
            elif not isinstance(context_method, str):
                context_method(self)
                return test_method(self, *args, **kwargs) 

        return new_test_method 

    def get_context_name(context):
        """ Get the context name from a context object.
        :param context: can be function or string
        """ 
        if isinstance(context, str):
            name = context
        else:
            name = context.__name__

        return name.replace('_', ' ')

    def func_consumer(test_method):
        for context_method in context_methods:
            test_method = get_new_test_method(test_method, context_method) 

        test_method.contexts = list(map(get_context_name, context_methods))
        return test_method

    return func_consumer


class TextTestResult(unittest.TestResult):
    """Changes test results to more readable form. It's alternative
    to unittest.TextTestResult. Used by TextTestRunner.
    """
    separator1 = '-' * 70
    separator2 = '-' * 70
    COLOR_GREEN = '\033[92m'
    COLOR_RED = '\033[91m'
    COLOR_END = '\033[0m'
    COLOR_BLUE = '\033[94m'

    def __init__(self, stream, descriptions, verbosity):
        super().__init__(stream, descriptions, verbosity)
        self.stream = stream
        self.showAll = verbosity > 1
        self.dots = verbosity == 1
        self.descriptions = descriptions
        self.analyzed_testcases = set()

    def _is_relevant_tb_level(self, tb):
        """Decide which frame in traceback will be shown at results, when
        some exception or error occurs. It hide frames from unittest module and
        from flowp.ftypes.Should class.

        Used by unittest.TestResult.
        """
        # Basic implementation from oryginal unittest.TestResult class
        if '__unittest' in tb.tb_frame.f_globals:
            return True

        # Additional implementation
        if 'self' in tb.tb_frame.f_locals:
            s = tb.tb_frame.f_locals['self']
            if hasattr(s, '_should_assert'):
                return True

        #
        return False

    def _testcase_name(self, test):
        return str(test).split()[1][1:-1]

    def _formatted_description(self, test):
        return '    - ' + self.getDescription(test) + ' ... '

    def _format_traceback_line(self, line):
        """Format single line of traceback
        :param str line:
            given traceback line
        """
        line = '  ' + line
        file_line = re.match(r'^\s*File "([\w/\.-]+)", line (\d+),', line)
        # reformat lines where is information about file and line number
        if file_line:
            return '  File "%s":%s' % (file_line.group(1), file_line.group(2))
        # remove first line of Traceback (which is not really necessary)
        elif re.match(r'^Traceback', line):
            return ''
        # changes last line to blue color
        elif re.match(r'^  \S', line):
            return self.COLOR_BLUE + line + self.COLOR_END
        else:
            return line

    def _format_traceback(self, traceback):
        """Format whole traceback. Eliminate unnecessary informations and
        add some colors.
        :param str traceback:
        """
        traceback = traceback.split("\n")[1:]
        traceback = map(self._format_traceback_line, traceback)
        traceback = "\n".join(traceback)
        return traceback

    def getDescription(self, test):
        """Get test name, it's method name from test case.
        Unlike oryginal method, it return name without test case name
        at the end and with replaced underscores to <space>.
        """
        return str(test).split()[0].replace('_', ' ')[3:]

    def startTest(self, test):
        """Print test group name (test case) if test is first in it's group.
        Results are visible in verbose mode as headers at test results.

        This assume that tests should be runned in order regarding to test case
        groups.
        """
        super().startTest(test)
        if self.showAll:
            testcase_name = self._testcase_name(test)
            if testcase_name not in self.analyzed_testcases:
                self.stream.writeln("\n%s:" % testcase_name)
                self.analyzed_testcases.add(testcase_name)

            self.stream.flush()

    def addSuccess(self, test):
        super().addSuccess(test)
        if self.showAll:
            self.stream.write(self.COLOR_GREEN)
            self.stream.write(self._formatted_description(test))
            self.stream.writeln("OK")
            self.stream.write(self.COLOR_END)
        elif self.dots:
            self.stream.write('.')
            self.stream.flush()

    def addError(self, test, err):
        super().addError(test, err)
        if self.showAll:
            self.stream.write(self.COLOR_RED)
            self.stream.write(self._formatted_description(test))
            self.stream.writeln("ERROR")
            self.stream.write(self.COLOR_END)
        elif self.dots:
            self.stream.write('E')
            self.stream.flush()

    def addFailure(self, test, err):
        super().addFailure(test, err)
        if self.showAll:
            self.stream.write(self.COLOR_RED)
            self.stream.write(self._formatted_description(test))
            self.stream.writeln("FAIL")
            self.stream.write(self.COLOR_END)
        elif self.dots:
            self.stream.write('F')
            self.stream.flush()

    def addSkip(self, test, reason):
        super().addSkip(test, reason)
        if self.showAll:
            self.stream.write(self.getDescription(test))
            self.stream.writeln("skipped {0!r}".format(reason))
        elif self.dots:
            self.stream.write("s")
            self.stream.flush()

    def addExpectedFailure(self, test, err):
        super().addExpectedFailure(test, err)
        if self.showAll:
            self.stream.write(self.getDescription(test))
            self.stream.writeln("expected failure")
        elif self.dots:
            self.stream.write("x")
            self.stream.flush()

    def addUnexpectedSuccess(self, test):
        super().addUnexpectedSuccess(test)
        if self.showAll:
            self.stream.write(self.getDescription(test))
            self.stream.writeln("unexpected success")
        elif self.dots:
            self.stream.write("u")
            self.stream.flush()

    def printErrors(self):
        if self.dots or self.showAll:
            self.stream.writeln()
        self.printErrorList('ERROR', self.errors)
        self.printErrorList('FAIL', self.failures)

    def printErrorList(self, flavour, errors):
        for test, err in errors:
            self.stream.writeln(self.separator1)
            self.stream.writeln()
            place = '"%s" [%s]' % (self.getDescription(test), 
                self._testcase_name(test))
            self.stream.write(self.COLOR_RED)
            self.stream.writeln("%s: %s" % (flavour, place))
            self.stream.write(self.COLOR_END)
            self.stream.writeln()
            self.stream.writeln("%s" % self._format_traceback(err))


class TestProgram(unittest.TestProgram):
    def _do_discovery(self, argv, Loader = None):
        """New _do_discovery method which takes into consideration 
        testLoader parameter from TestProgram.__init__ method, when 
        discover mode is given. It discover test cases.

        In oryginal version of this method (from unittest module), 
        custom loader is ignored when discover mode is given (bug?).
        """
        if not Loader:
            Loader = type(self.testLoader)
        super()._do_discovery(argv, Loader)


class TestLoader(unittest.TestLoader):
    """Changes prefixes for test files and test methods. Test methods,
    behaviors should start with 'it' and test files with 'spec'
    """
    testMethodPrefix = 'it'

    def discover(self, start_dir, pattern='spec*.py', top_level_dir=None):
        # Force spec pattern
        pattern = 'spec*.py'
        return super().discover(start_dir, pattern, top_level_dir) 


class TextTestRunner(unittest.TextTestRunner):
    """Set custom flowp test result class"""
    resultclass = TextTestResult


# Allow to run flowp.testing module as a script. It behaves like 
# unittest.main script module.
main = TestProgram

if __name__ == '__main__':
    sys.argv[0] = "python3 -m flowp.testing"
    loader = TestLoader()
    main(module=None, testLoader=loader, testRunner=TextTestRunner)
