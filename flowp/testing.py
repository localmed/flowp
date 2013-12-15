import unittest
import re
import contextlib
import inspect
import os
from collections import OrderedDict
import tempfile
import time
import sys
import imp
import glob
import subprocess

class colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    END = '\033[0m'

class BDDTestCase(type):
    """Meta class for test case class (Behavior). Creates aliases 
    for setUp and tearDown methods: before_each and after_each.
    """
    def __new__(cls, name, bases, namespace):
        new_namespace = {}
        for key, value in namespace.items():
            if key == 'before_each':
                new_namespace['setUp'] = value

            if key == 'after_each':
                new_namespace['tearDown'] = value

            new_namespace[key] = value

        return type.__new__(cls, name, bases, new_namespace)


class Behavior(unittest.TestCase, metaclass=BDDTestCase):
    @property
    def _test_method(self):
        """Return object of (current) test method."""
        return getattr(self, self._testMethodName) 


class FileSystemBehavior(Behavior):
    """Test case with basic setup for filesystem testing. It creates
    temporary directory and changes current working directory to it.
    After each test, returns to primary 'cwd' and remove temporary directory.
    """
    def before_each(self):
        self.tempdir = TemporaryDirectory()
        self.tempdir.enter()

    def after_each(self):
        self.tempdir.exit()
        self.tempdir.cleanup()

    def reset_cwd(self):
        os.chdir(self.tempdir.name)


class expect:
    # Flag which says that this class should be omitted in test result tracebacks
    _pass_unittest_traceback = True

    def __init__(self, context):
        self._context = context
        self._expected_exception = None

    @property
    def ok(self):
        """expect(a).ok"""
        assert self._context,\
            "expected %s, given %s" % (True, self._context)    

    @property
    def not_ok(self):
        """expect(a).not_ok"""
        assert not self._context,\
            "expected not %s, given %s" % (True, self._context)    

    def __eq__(self, expectation):
        """expect(a) == b"""
        assert self._context == expectation,\
            "expected %s, given %s" % (expectation, self._context)

    def __ne__(self, expectation):
        """expect(a) != b"""
        assert self._context != expectation,\
            "expected %s != %s" % (self._context, expectation)

    def __lt__(self, expectation):
        """expect(a) < b"""
        assert self._context < expectation,\
            "expected %s < %s" % (self._context, expectation)

    def __le__(self, expectation):
        """expect(a) <= b"""
        assert self._context <= expectation,\
            "expected %s <= %s" % (self._context, expectation)

    def __gt__(self, expectation):
        """expect(a) > b"""
        assert self._context > expectation,\
            "expected %s > %s" % (self._context, expectation)

    def __ge__(self, expectation):
        """expect(a) >= b"""
        assert self._context >= expectation,\
            "expected %s >= %s" % (self._context, expectation)

    def isinstance(self, expectation):
        assert isinstance(self._context, expectation),\
            "expected %s, given %s" % (expectation, type(self._context))

    def not_isinstance(self, expectation):
        assert not isinstance(self._context, expectation),\
            "expected not %s, given %s" % (expectation, type(self._context))
    
    def be_in(self, expectation):
        assert self._context in expectation,\
            "%s not in %s" % (self._context, expectation)

    def not_be_in(self, expectation):
        assert self._context not in expectation,\
            "%s in %s" % (self._context, expectation)

    def be(self, expectation):
        assert self._context is expectation,\
            "%s is not %s" % (self._context, expectation)

    def not_be(self, expectation):
        assert self._context is not expectation,\
            "%s is %s" % (self._context, expectation)

    def to_raise(self, expected_exception):
        self._expected_exception = expected_exception
        return self

    def by_call(self, *args, **kwargs):
        try:
            self._context(*args, **kwargs)
            raise AssertionError("%s exception should be raised" % \
                self._expected_exception.__name__)
        except self._expected_exception:
            pass 

    @property
    def called(self):
        assert self._context.called 

    @property
    def not_called(self):
        assert not self._context.called

    def called_with(self, *args, **kwargs):
        self._context.assert_any_call(*args, **kwargs)


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
            # if context have annotations, create name from them
            if hasattr(context, '__annotations__') and\
                context.__annotations__.get('return'):
                name = context.__annotations__.get('return') 
            else:
                name = context.__name__

        return name.replace('_', ' ')

    def func_consumer(test_method):
        for context_method in context_methods:
            test_method = get_new_test_method(test_method, context_method) 

        test_method.contexts = list(map(get_context_name, context_methods))
        return test_method

    return func_consumer


class ContextsTree:
    """Tree structure used by TestSuite.addTests. From list of tests
    create tree which is made by OrderedDict. In the tree it group the tests
    by tests contexts, provided by 'when' decorator. Thanks to this, contexts
    with tests can be printed in test results in groups, apart from the order
    of used 'when' decorators in test case code.

    Example of tree structure:
    {
        None: [func1, func2],
        'ctx1': {
            None: [func3, func4],
            'ctx2': {None: [func5, func6]}
        },
        'ctx3': {None: [func6]}
    }

    Keys of dictionaries represents contexts, values subtree (another 
    dictionaries) or leafs (lists). None keys represents tree leafs.
    """
    def __init__(self, test_cases):
        self.structure = OrderedDict({None: []})
        self.build_tree(test_cases)

    def build_tree(self, test_cases):
        """Build tree by given test cases sequence and tests contexts.
        :param test_cases:
            Sequence of flowp.testing.Behavior instances (test cases).
            Each test case represents environment of single test method.
        """
        for test_case in test_cases:
            # if it's not test case (it's test suite), pass it
            if not hasattr(test_case, '_test_method'):
                self.structure[None].append(test_case)
                continue

            # if test method have 'when' contexts
            if hasattr(test_case._test_method, 'contexts'):
                subtree = self.structure
                for context in test_case._test_method.contexts:
                    # if context not found in subtree, make a node of this ctx
                    if context not in subtree.keys():
                        subtree[context] = OrderedDict({None: []})
                    
                    # if context is last at the list, set test to it
                    if context == test_case._test_method.contexts[-1]:
                        subtree[context][None].append(test_case)

                    # if not, enter to subtree of this context
                    else:
                        subtree = subtree[context]

            # if test method doesn't have 'when' contexts (regular test)
            else:
                self.structure[None].append(test_case)

    def _get_list(self, subtree):
        l = []
        for key in subtree:
            if key == None:
                l.extend(subtree[key])
            else:
                l.extend(self._get_list(subtree[key]))
        return l

    @property
    def list(self):
        """Transform tree to the list and return it. Items in the list
        are sorted by test contexts.
        """
        return self._get_list(self.structure) 


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


    def __init__(self, stream, descriptions, verbosity, nocolors=False):
        super().__init__(stream, descriptions, verbosity)
        self.stream = stream
        self.showAll = verbosity > 1
        self.dots = verbosity == 1
        self.descriptions = descriptions
        self.nocolors = nocolors
        self.analyzed_testcases = set()
        self.analyzed_contexts = set()

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
            if hasattr(s, '_pass_unittest_traceback'):
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
            if self.nocolors:
                return line
            else:
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

    def _get_test_method_contexts(self, test):
        """Return currently considered test method contexts."""
        if hasattr(test._test_method, 'contexts'):
            return test._test_method.contexts
        return []

    def getDescription(self, test):
        """Get test name, it's method name from test case.
        Unlike oryginal method, it return name without test case name
        at the end and with replaced underscores to <space>.
        """
        if type(test).__name__ == 'ModuleImportFailure':
            return str(test).split()[0]
        else: 
            return str(test).split()[0].replace('_', ' ')[3:]

    def startTest(self, test):
        """Print test group name (test case) if test is first in it's group.
        Results are visible in verbose mode as headers at test results.

        This assume that tests should be runned in order regarding to the 
        test case groups.

        It also prints test contexts in groups.
        """
        super().startTest(test)
        if self.showAll:
            # printing test case name as a header
            testcase_name = self._testcase_name(test)
            if testcase_name not in self.analyzed_testcases:
                self.stream.writeln("\n\n%s:" % testcase_name)
                self.analyzed_testcases.add(testcase_name)

            if not type(test).__name__ == 'ModuleImportFailure':
                # analyzing contexts names list of current test
                contexts_path = [] 
                for context in self._get_test_method_contexts(test):
                    contexts_path.append(context)
                    # print contexts names as headers
                    if tuple(contexts_path) not in self.analyzed_contexts:
                        self.stream.write("\n" + '    ' * len(contexts_path))
                        self.stream.writeln('when %s:' % context)
                        self.analyzed_contexts.add(tuple(contexts_path))

                # determining indent (regarding to contexts)
                for context in self._get_test_method_contexts(test):
                    self.stream.write('   ')

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
            if not self.nocolors:
                self.stream.write(self.COLOR_RED)
            self.stream.writeln("%s: %s" % (flavour, place))
            if not self.nocolors:
                self.stream.write(self.COLOR_END)
            self.stream.writeln()
            self.stream.writeln("%s" % self._format_traceback(err))


class TestSuite(unittest.TestSuite):
    def addTests(self, tests):
        """Add sorted tests by contexts to the test suite"""
        super().addTests(ContextsTree(tests).list) 


class TestLoader(unittest.TestLoader):
    """Changes prefixes for test files and test methods. Test methods,
    behaviors should start with 'it' and test files with 'spec'. It also
    changes suiteClass.
    """
    testMethodPrefix = 'it'
    suiteClass = TestSuite

    def discover(self, start_dir, pattern='spec*.py', top_level_dir=None):
        # Force spec pattern
        pattern = 'spec*.py'
        return super().discover(start_dir, pattern, top_level_dir)


class ColorWriteDecorator:
    """Used to decorate file-like objects with a handy 'writeln' method"""
    def __init__(self,stream):
        self.stream = stream

    def __getattr__(self, attr):
        if attr in ('stream', '__getstate__'):
            raise AttributeError(attr)
        return getattr(self.stream,attr)

    def write(self, arg):
        if arg:
            if arg=='OK':
                self.stream.write(colors.GREEN + arg + colors.END)
            elif arg=='FAILED':
                self.stream.write(colors.RED + arg + colors.END)
            else:
                self.stream.write(arg)


class TextTestRunner(unittest.TextTestRunner):
    """Set custom flowp test result class"""
    resultclass = TextTestResult

    def __init__(self, stream=None, descriptions=True, verbosity=1, failfast=False,
                 buffer=False, resultclass=None, warnings=None, nocolors=False):
        super().__init__(stream, descriptions, verbosity, failfast, buffer, resultclass, warnings)
        self.nocolors = nocolors
        if not nocolors:
            self.stream = ColorWriteDecorator(self.stream)

    def _makeResult(self):
        return self.resultclass(self.stream, self.descriptions, self.verbosity,
                                self.nocolors)


class TemporaryDirectory(tempfile.TemporaryDirectory):
    def enter(self):
        self.org_cwd = os.getcwd()
        os.chdir(self.name)

    def exit(self):
        os.chdir(self.org_cwd)


class TestProgram(unittest.TestProgram):
    AUTORUN_TIME_INTERVAL = 4

    def __init__(self, module='__main__', defaultTest=None, argv=None, testRunner=None,
                 testLoader=TestLoader, exit=True, verbosity=1, failfast=None,
                 catchbreak=None, buffer=None, warnings=None, autorun=False,
                 nocolors=False):
        self.nocolors = nocolors
        self.autorun = autorun
        super().__init__(module, defaultTest, argv, testRunner, testLoader, exit, verbosity,
                         failfast, catchbreak, buffer, warnings)

    RUN_MODULE = 'flowp.testing'

    def _getOptParser(self):
        parser = super()._getOptParser()
        parser.add_option('-a', '--autorun', dest='autorun', default=False, help='Auto run',
                          action='store_true')
        parser.add_option('--nocolors', dest='nocolors', default=False,
                          help='Print results without colors', action='store_true')
        return parser

    def _setAttributesFromOptions(self, options):
        super()._setAttributesFromOptions(options)
        if options.autorun:
            self.autorun = options.autorun
        if options.nocolors:
            self.nocolors = options.nocolors

    def runTests(self):
        if self.catchbreak:
            installHandler()
        if self.testRunner is None:
            self.testRunner = runner.TextTestRunner
        if isinstance(self.testRunner, type):
            try:
                testRunner = self.testRunner(verbosity=self.verbosity,
                                             failfast=self.failfast,
                                             buffer=self.buffer,
                                             warnings=self.warnings,
                                             nocolors=self.nocolors)
            except TypeError:
                # didn't accept the verbosity, buffer or failfast arguments
                testRunner = self.testRunner()
        else:
            # it is assumed to be a TestRunner instance
            testRunner = self.testRunner
        self.result = testRunner.run(self.test)
        if self.exit:
            sys.exit(not self.result.wasSuccessful())

    @classmethod
    def create(cls, *args, **kwargs):
        """When found autorun option, factory method run loop, where rerun
        tests at some time interval.
        """
        program = cls(*args, **kwargs)

        if hasattr(program, 'autorun') and program.autorun:
            try:
                if 'argv' in kwargs:
                    argv = kwargs['argv']
                else:
                    argv = sys.argv
                if '-a' in argv:
                    argv.remove('-a')
                if '--auto' in argv:
                    argv.remove('--auto')
                argv = [sys.executable, '-m', cls.RUN_MODULE] + argv[1:]

                while True:
                    time.sleep(cls.AUTORUN_TIME_INTERVAL)
                    subprocess.call(argv)
            except KeyboardInterrupt:
                pass


if __name__ == '__main__':
    TestProgram.create(module=None, testLoader=TestLoader(), testRunner=TextTestRunner,
                       exit=False)
