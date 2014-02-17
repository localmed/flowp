import glob
import os.path
import re
import importlib
import sys
import inspect
import traceback
import time
from unittest import mock

# for traceback passing in test results
TESTING_MODULE = True


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


def only(func):
    func.only_mode = True
    return func


def skip(func):
    func.skipped = True
    return func


class Behavior:
    """Test case"""
    parent_behaviors = tuple()

    def __init__(self, method_name, results):
        self.method_name = method_name
        self._results = results

    def before_each(self):
        pass

    def after_each(self):
        pass

    def run(self, only_mode=False):
        """Run specific test"""
        method = getattr(self, self.method_name)
        self._results.start_test()
        if only_mode and not hasattr(method, 'only_mode'):
            self._results.add_skipped()
            return None
        if hasattr(method, 'skipped'):
            self._results.add_skipped()
            return None
        try:
            self._results.add_executed()
            # run before methods
            for parent_behavior in self.parent_behaviors:
                parent_behavior.before_each(self)
            self.before_each()
            # run test method
            method()
            # run after methods
            self.after_each()
            for parent_behavior in reversed(self.parent_behaviors):
                parent_behavior.after_each(self)
            # stop patchers
            mock.patch.stopall()
        except:
            self._results.add_failure(sys.exc_info(), self)
        else:
            self._results.add_success()

    def mock(self, target=None, attr=None, new=mock.DEFAULT, spec=None):
        """Create a mock and register it at behavior mocks manager.

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
            unittest.mock.Mock if new==None
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
        self.started = 0
        self.executed = 0

    def start_test(self):
        self.started += 1

    def stop_test(self):
        pass

    def add_success(self):
        pass

    def add_skipped(self):
        self.skipped += 1

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

    def print(self, time_taken):
        # failures
        for err, behavior in self.failures:
            method_name = behavior.method_name[3:].replace('_', ' ')
            description = self.get_behaviors_description(behavior) + ' ' + method_name
            self.stream.red("\n%s FAILED\n" % description)
            self.stream.write("%s\n" % err)

        # sum up
        failures = len(self.failures)
        self.stream.write('Executed %s of %s ' % (self.executed, self.started))
        if self.skipped:
            self.stream.write('(%s skipped) ' % self.skipped)
        if failures:
            self.stream.red('(%s FAILED) ' % failures)
        else:
            self.stream.green('SUCCESS ')
        self.stream.writeln('(%.3f sec)' % time_taken)

        # Executed 10 of 123 (skipped 113) SUCCESS (3.450 sec)
        # Executed 10 of 123 (1 FAILED) (skipped 113) (3.450 sec)

        # test should have be alone FAILED

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
        return 'TESTING_MODULE' in tb.tb_frame.f_globals


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
        files = glob.glob('**/%s*.py' % self.spec_file_prefix)
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
        for attr_name in dir(behavior_class):
            if attr_name.startswith('_'):
                continue
            attr = getattr(behavior_class, attr_name)
            if self.is_test_function(attr):
                behavior = behavior_class(attr_name, results)
                self.loaded_tests.append(behavior)
                if hasattr(attr, 'only_mode'):
                    self.only_mode = True
            elif self.is_behavior_class(attr):
                attr.parent_behaviors = \
                    behavior_class.parent_behaviors + (behavior_class,)
                self.load_tests(attr, results)

    def run(self):
        """Looking for behavior subclasses in modules"""
        results = Results()
        start_time = time.time()
        # Load tests
        for module in self.get_spec_modules():
            for BClass in self.get_behavior_classes(module):
                self.load_tests(BClass, results)
        # Run tests
        for behavior in self.loaded_tests:
            behavior.run(self.only_mode)
        stop_time = time.time()
        time_taken = stop_time - start_time
        results.print(time_taken)


class expect:
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
                "expected %s, given %s" % (True, self._context)
        else:
            assert self._context is expectation, \
                "%s is not %s" % (self._context, expectation)

    def not_to_be(self, expectation):
        if isinstance(expectation, bool):
            assert not bool(self._context) == expectation, \
                "expected not %s, given %s" % (True, self._context)
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
