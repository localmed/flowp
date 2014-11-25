import os.path
import re
import importlib
import sys
import inspect
import traceback
import time
import tempfile
import argparse
import subprocess
from unittest import mock
from glob2 import glob
from junit_xml import TestSuite, TestCase
from flowp import files

# for traceback passing in test results
TESTING_FRAME = True


class ColorStream(str):
    GREEN = '\033[92m'
    RED = '\033[91m'
    COLOR_END = '\033[0m'

    def __init__(self, stream):
        self._stream = stream

    def write(self, msg):
        self._stream.write(msg)

    def writeln(self, msg=''):
        self._stream.write(msg + '\n')

    def red(self, msg):
        self._stream.write(self.RED + msg + self.COLOR_END)

    def green(self, msg):
        self._stream.write(self.GREEN + msg + self.COLOR_END)

    def redln(self, msg):
        self.red(msg)
        self.writeln()

    def greenln(self, msg):
        self.green(msg)
        self.writeln()

    def flush(self):
        self._stream.flush()


def only(obj):
    obj._only_mode = True
    return obj


def skip(obj):
    obj._skipped = True
    return obj


def slow(obj):
    obj._slow = True
    return obj


class TemporaryDirectory:
    """tempfile.TemporaryDirectory proxy"""
    def __init__(self):
        self._tmpdir = None
        self._org_cwd = None

    def enter(self):
        """Create temporary directory and set current working
        directory to it, remembering the original one.
        """
        self._org_cwd = os.getcwd()
        self._tmpdir = tempfile.TemporaryDirectory()
        os.chdir(self._tmpdir.name)

    def exit(self):
        """Set current working directory to the original one and
        cleanup temporary directory.
        """
        if not self._tmpdir:
            return None
        os.chdir(self._org_cwd)
        self._tmpdir.cleanup()

    @property
    def name(self):
        return self._tmpdir.name


class Behavior:
    """Test case"""
    parent_behaviors = tuple()

    def __init__(self, method_name, results):
        self.method_name = method_name
        self._results = results
        self.tmpdir = TemporaryDirectory()

    def _have_only_mode(self):
        if hasattr(self, '_only_mode'):
            return True
        for pbehavior in self.parent_behaviors:
            if hasattr(pbehavior, '_only_mode'):
                return True
        return False

    def _is_skipped(self):
        if hasattr(self, '_skipped'):
            return True
        for pbehavior in self.parent_behaviors:
            if hasattr(pbehavior, '_skipped'):
                return True
        return False

    def _is_slow(self):
        if hasattr(self, '_slow'):
            return True
        for pbehavior in self.parent_behaviors:
            if hasattr(pbehavior, '_slow'):
                return True
        return False

    def before_each(self):
        pass

    def after_each(self):
        pass

    def _call_before_each_methods(self):
        for parent_behavior in self.parent_behaviors:
            parent_behavior.before_each(self)
        self.before_each()

    def _call_after_each_methods(self):
        self.after_each()
        for parent_behavior in reversed(self.parent_behaviors):
            parent_behavior.after_each(self)

    def run(self, only_mode=False, fast_mode=False):
        """Run specific test"""
        method = getattr(self, self.method_name)
        self._results.start_test()
        if only_mode and (not hasattr(method, '_only_mode') and
                          not self._have_only_mode()):
            self._results.add_skipped(self)
            return None
        if self._is_skipped() or hasattr(method, '_skipped'):
            self._results.add_skipped(self)
            return None
        if fast_mode and (hasattr(method, '_slow') or
                          self._is_slow()):
            self._results.add_skipped_slow(self)
            return None

        try:
            self._results.add_executed()
            self._call_before_each_methods()
            method()

        # Catching exceptions
        except:
            try:
                self._call_after_each_methods()
                mock.patch.stopall()
            except:
                self._results.add_failure(sys.exc_info(), self)
            else:
                self._results.add_failure(sys.exc_info(), self)
        else:
            try:
                self._call_after_each_methods()
                mock.patch.stopall()
            except:
                self._results.add_failure(sys.exc_info(), self)
            else:
                self._results.add_success(self)
        finally:
            if self._results.executed < self._results.all:
                self._results.print_execution_info(in_place=True)

    def mock(self, target=None, attr=None, new=mock.DEFAULT, spec=None):
        """Create a mock and register it in behavior mocks manager.

        :param target:
            place to patch
        :param attr:
            name of attribute to patch (used only when target
            is an object instance)
        :param new:
            object which will be returned instead of default mock
            (used only when target is given)
        :param spec:
            list of attributes which mock should have
        :rtype:
            unittest.mock.Mock if new will have default value
        """
        patcher = None
        if target and attr:
            patcher = mock.patch.object(target, attr, new=new, spec=spec)
        elif target:
            if not isinstance(target, str):
                raise TypeError("If attr not given target should be a string, %s given" %
                                type(target))
            patcher = mock.patch(target, new=new, spec=spec)

        if patcher:
            return patcher.start()
        return mock.Mock(spec=spec)


class Results:
    """Gather informations about test results"""
    def __init__(self):
        self.stream = ColorStream(sys.stdout)
        self.failures = []
        self.skipped = 0
        self.executed = 0
        self.all = 0
        self.skipped_slow = 0

    def start_test(self):
        pass

    def stop_test(self):
        pass

    def add_success(self, behavior):
        pass

    def add_skipped(self, behavior):
        self.skipped += 1

    def add_skipped_slow(self, behavior):
        self.skipped_slow += 1

    def add_executed(self):
        self.executed += 1

    def add_failure(self, exc_info, behavior):
        self.failures.append((self._exc_info_to_string(exc_info), behavior))

    def get_behaviors_description(self, behavior: Behavior):
        description = ''

        for parent_behavior in behavior.parent_behaviors:
            description += parent_behavior.__name__

        description += behavior.__class__.__name__
        # Transform camel case to spaces
        description = re.sub('([a-z0-9])([A-Z])', r'\1 \2', description).lower().capitalize()
        return description

    def print_execution_info(self, in_place=False):
        failures = len(self.failures)
        if in_place:
            self.stream.write('\r')
        self.stream.write('Executed %s of %s ' % (self.executed, self.all))
        if self.skipped:
            self.stream.write('(%s skipped) ' % self.skipped)
        if self.skipped_slow:
            self.stream.write('(%s too slow) ' % self.skipped_slow)
        if failures:
            self.stream.red('(%s FAILED) ' % failures)
        else:
            self.stream.green('SUCCESS ')

    def print(self, time_taken):
        # clean line
        self.stream.write('\r')
        if self.failures:
            self.stream.write(' ' * 80)

        # failures
        for err, behavior in self.failures:
            method_name = behavior.method_name[3:].replace('_', ' ')
            description = self.get_behaviors_description(behavior) + ' ' + method_name
            self.stream.red("\n%s FAILED\n" % description)
            self.stream.write("%s\n" % err)

        # sum up
        self.print_execution_info()
        self.stream.writeln('(%.3f sec)' % time_taken)

    def _exc_info_to_string(self, err):
        """Converts a sys.exc_info()-style tuple of values into a string."""
        exctype, value, tb = err
        # Skip test runner traceback levels
        while tb and self._is_relevant_tb_level(tb):
            tb = tb.tb_next
        length = self._count_relevant_tb_levels(tb)
        msg_lines = traceback.format_exception(exctype, value, tb, length)[1:]
        msg_lines[-1] = '  ' + msg_lines[-1]
        msg_lines = ''.join(msg_lines)
        return msg_lines

    def _count_relevant_tb_levels(self, tb):
        length = 0
        while tb and not self._is_relevant_tb_level(tb):
            length += 1
            tb = tb.tb_next
        return length

    def _is_relevant_tb_level(self, tb):
        if 'TESTING_FRAME' in tb.tb_frame.f_globals:
            return True

        if 'self' in tb.tb_frame.f_locals:
            obj = tb.tb_frame.f_locals['self']
            if hasattr(obj, 'TESTING_FRAME'):
                return True

        return False


class JunitResults(Results):
    """Gather informations about test results"""
    def __init__(self):
        super().__init__()
        self.junit_cases = []

    def add_success(self, behavior):
        super().add_success(behavior)
        test_case = TestCase(self.get_behaviors_description(behavior))
        self.junit_cases.append(test_case)

    def add_skipped(self, behavior):
        super().add_skipped(behavior)
        test_case = TestCase(self.get_behaviors_description(behavior))
        test_case.add_skipped_info(message='Skipped')
        self.junit_cases.append(test_case)

    def add_skipped_slow(self, behavior):
        super().add_skipped_slow(behavior)
        test_case = TestCase(self.get_behaviors_description(behavior))
        test_case.add_skipped_info(message='Test ran too slowly and was skipped.')
        self.junit_cases.append(test_case)

    def add_failure(self, exc_info, behavior):
        super().add_failure(exc_info, behavior)
        test_case = TestCase(self.get_behaviors_description(behavior))
        test_case.add_failure_info(message='Test Failed', output=self._exc_info_to_string(exc_info))
        self.junit_cases.append(test_case)

    def print(self, time_taken):
        super().print(time_taken)
        test_suite = TestSuite("Test Results", self.junit_cases)
        with open('output.xml', 'w') as f:
            TestSuite.to_file(f, [test_suite], prettyprint=True)


class Runner:
    """Parse script arguments and run tests"""
    test_method_prefix = 'it_'
    spec_file_prefix = 'spec_'
    behavior_cls = Behavior

    def __init__(self):
        self.loaded_tests = []
        self.only_mode = False

    def is_behavior_class(self, obj):
        return inspect.isclass(obj) and \
            issubclass(obj, self.behavior_cls)

    def is_test_function(self, obj):
        return inspect.isfunction(obj) and \
            obj.__name__.startswith(self.test_method_prefix)

    def get_spec_modules(self):
        """Get modules to tests"""
        files = glob('**/%s*.py' % self.spec_file_prefix)
        for fn in files:
            fn = fn.replace(os.path.sep, '.')
            mn = re.sub('\.py$', '', fn)
            yield importlib.import_module(mn)

    def get_behavior_classes(self, module):
        for attr_name in dir(module):
            attr = getattr(module, attr_name)
            if self.is_behavior_class(attr):
                yield attr

    def load_tests(self, behavior_class, results: Results):
        """Load tests from behavior class"""
        if hasattr(behavior_class, '_only_mode'):
            self.only_mode = True
        for attr_name in dir(behavior_class):
            if attr_name.startswith('_'):
                continue
            attr = getattr(behavior_class, attr_name)
            if self.is_test_function(attr):
                behavior = behavior_class(attr_name, results)
                self.loaded_tests.append(behavior)
                if hasattr(attr, '_only_mode'):
                    self.only_mode = True
            elif self.is_behavior_class(attr):
                attr.parent_behaviors = \
                    behavior_class.parent_behaviors + (behavior_class,)
                self.load_tests(attr, results)

    def run(self, fast_mode=False, junit=False):
        """Looking for behavior subclasses in modules"""
        results = JunitResults() if junit else Results()
        start_time = time.time()
        # Load tests
        for module in self.get_spec_modules():
            for BClass in self.get_behavior_classes(module):
                self.load_tests(BClass, results)
        results.all = len(self.loaded_tests)

        # Run tests
        for behavior in self.loaded_tests:
            behavior.run(self.only_mode, fast_mode)

        # Print results
        stop_time = time.time()
        time_taken = stop_time - start_time
        results.print(time_taken)


class expect:
    # for passing traceback purpose
    TESTING_FRAME = True

    class to_raise:
        def __init__(self, expected_exc):
            self.expected_exc = expected_exc

        def __enter__(self):
            pass

        def __exit__(self, exc_type, exc_val, exc_tb):
            if exc_type is not self.expected_exc:
                raise AssertionError("expected exception %s"
                                     % self.expected_exc.__name__)
            return True

    def __init__(self, context):
        self._context = context
        self._expected_exception = None

    def to_be(self, expectation):
        if isinstance(expectation, bool):
            assert bool(self._context) == expectation, \
                "expected %s, given %s" % (expectation, self._context)
        else:
            assert self._context is expectation, \
                "%s is not %s" % (self._context, expectation)

    def not_to_be(self, expectation):
        if isinstance(expectation, bool):
            assert not bool(self._context) == expectation, \
                "expected not %s, given %s" % (expectation, self._context)
        else:
            assert self._context is not expectation, \
                "%s is %s" % (self._context, expectation)

    def __eq__(self, expectation):
        """expect(a) == b"""
        assert self._context == expectation, \
            "expected %s, given %s" % (expectation, self._context)

    def __ne__(self, expectation):
        """expect(a) != b"""
        assert self._context != expectation, \
            "expected %s != %s" % (self._context, expectation)

    def __lt__(self, expectation):
        """expect(a) < b"""
        assert self._context < expectation, \
            "expected %s < %s" % (self._context, expectation)

    def __le__(self, expectation):
        """expect(a) <= b"""
        assert self._context <= expectation, \
            "expected %s <= %s" % (self._context, expectation)

    def __gt__(self, expectation):
        """expect(a) > b"""
        assert self._context > expectation, \
            "expected %s > %s" % (self._context, expectation)

    def __ge__(self, expectation):
        """expect(a) >= b"""
        assert self._context >= expectation, \
            "expected %s >= %s" % (self._context, expectation)

    def to_be_instance_of(self, expectation):
        assert isinstance(self._context, expectation), \
            "expected %s, given %s" % (expectation, type(self._context))

    def not_to_be_instance_of(self, expectation):
        assert not isinstance(self._context, expectation), \
            "expected not %s, given %s" % (expectation, type(self._context))

    def to_be_in(self, expectation):
        assert self._context in expectation, \
            "%s not in %s" % (self._context, expectation)

    def not_to_be_in(self, expectation):
        assert self._context not in expectation, \
            "%s in %s" % (self._context, expectation)

    def to_have_been_called(self, count=None):
        if isinstance(count, int):
            assert self._context.call_count == count, \
                "expected %s mock calls, actual %s" % \
                (count, self._context.call_count)
        else:
            assert self._context.called

    def not_to_have_been_called(self):
        assert not self._context.called

    def to_have_been_called_with(self, *args, **kwargs):
        self._context.assert_any_call(*args, **kwargs)


class Script:
    def __init__(self):
        parser = argparse.ArgumentParser()
        parser.add_argument('--watch', action='store_true')
        parser.add_argument('--fast', action='store_true')
        parser.add_argument('--junit', action='store_true')
        self.args = parser.parse_args()

    def watch_callback(self, filename, action):
        args = [sys.executable, '-m', 'flowp.testing']
        if self.args.fast:
            args.append('--fast')
        subprocess.call(args)

    def run(self):
        Runner().run(fast_mode=self.args.fast, junit=self.args.junit)
        if self.args.watch:
            files.Watch(['*.py', '**/*.py'], self.watch_callback).wait()
