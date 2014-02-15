import glob
import os.path
import re
import importlib
import sys
import inspect
import logging
import traceback

# for traceback passing in test results
TESTING_MODULE = True


class Behavior:
    """Test case"""
    parent_behavior = None

    def before_each(self):
        pass

    def after_each(self):
        pass


class ColorLogger:
    GREEN = '\033[92m'
    RED = '\033[91m'
    COLOR_END = '\033[0m'

    def __init__(self):
        formatter = logging.Formatter('%(message)s')
        handler = logging.StreamHandler()
        handler.setLevel(logging.DEBUG)
        handler.setFormatter(formatter)
        self._logger = logging.getLogger('ColorLogger')
        self._logger.setLevel(logging.DEBUG)
        self._logger.addHandler(handler)

    def error(self, msg):
        self._logger.error(self.RED + msg + self.COLOR_END)

    def info(self, msg):
        self._logger.info(msg)

    def success(self, msg):
        self._logger.info(self.GREEN + msg + self.COLOR_END)


class Results:
    """Gather informations about test results"""
    def __init__(self, logger):
        self.logger = logger
        self.failures = []
        self.errors = []
        self.skipped = []
        self.runned_tests_count = 0

    def start_test(self):
        self.runned_tests_count += 1

    def stop_test(self):
        pass

    def add_success(self):
        pass

    def add_failure(self, exc_info, method_name, behavior):
        self.failures.append((self._exc_info_to_string(exc_info), method_name, behavior))

    def add_error(self, exc_info, method_name, behavior):
        self.errors.append((self._exc_info_to_string(exc_info), method_name, behavior))

    def get_behaviors_description(self, behavior):
        description = ''
        if behavior.parent_behavior:
            description += self.get_behaviors_description(behavior.parent_behavior)

        if inspect.isclass(behavior):
            description += behavior.__name__
        else:
            description += behavior.__class__.__name__
        return description

    def print_errors(self):
        self.print_error_list('ERROR', self.errors)
        self.print_error_list('FAIL', self.failures)

    def print_error_list(self, flavour, errors):
        for err, method_name, behavior in errors:
            description = self.get_behaviors_description(behavior) + ' ' + method_name
            self.logger.info('----')
            self.logger.info("%s: %s" % (flavour, description))
            self.logger.info('----')
            self.logger.info("%s" % err)

    def print_sum_up(self):
        errors, failures = len(self.errors), len(self.failures)
        if not errors and not failures:
            self.logger.success('TESTS OK')
        else:
            self.logger.error('TESTS FAILED')

    def _exc_info_to_string(self, err):
        """Converts a sys.exc_info()-style tuple of values into a string."""
        exctype, value, tb = err
        # Skip test runner traceback levels
        while tb and self._is_relevant_tb_level(tb):
            tb = tb.tb_next
        length = self._count_relevant_tb_levels(tb)
        msg_lines = traceback.format_exception(exctype, value, tb, length)
        return ''.join(msg_lines)

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
        pass

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

    def is_behavior_class(self, obj):
        return inspect.isclass(obj) and issubclass(obj, self.behavior_cls)

    def is_test_function(self, obj):
        return inspect.isfunction(obj) and obj.__name__.startswith(self.test_method_prefix)

    def run_before_each_methods(self, behavior_instance, behavior_class=None):
        if behavior_class:
            if behavior_class.parent_behavior:
                self.run_before_each_methods(behavior_instance, behavior_class.parent_behavior)
            behavior_class.before_each(behavior_instance)
        else:
            if behavior_instance.parent_behavior:
                self.run_before_each_methods(behavior_instance, behavior_instance.parent_behavior)
            behavior_instance.before_each()

    def run_after_each_methods(self, behavior_instance, behavior_class=None):
        if behavior_class:
            behavior_class.after_each(behavior_instance)
            if behavior_class.parent_behavior:
                self.run_after_each_methods(behavior_instance, behavior_class.parent_behavior)
        else:
            behavior_instance.after_each()
            if behavior_instance.parent_behavior:
                self.run_after_each_methods(behavior_instance, behavior_instance.parent_behavior)

    def run_test_method(self, method_name, results: Results, behavior: Behavior):
        method = getattr(behavior, method_name)
        results.start_test()
        try:
            self.run_before_each_methods(behavior)
            method()
            self.run_after_each_methods(behavior)
        except AssertionError:
            results.add_failure(sys.exc_info(), method_name, behavior)
        except:
            results.add_error(sys.exc_info(), method_name, behavior)
        else:
            results.add_success()

    def run_behavior(self, behavior_class, results: Results):
        for attr_name in dir(behavior_class):
            attr = getattr(behavior_class, attr_name)
            if self.is_test_function(attr):
                print("#2 Executing %s" % attr_name)
                behavior = behavior_class()
                # Executing test method
                self.run_test_method(attr_name, results, behavior)
            elif self.is_behavior_class(attr):
                attr.parent_behavior = behavior_class
                self.run_behavior(attr, results)

    def run(self):
        logger = ColorLogger()
        results = Results(logger)
        for module in self.get_spec_modules():
            for BClass in self.get_behavior_classes(module):
                print('#1', BClass, module)
                self.run_behavior(BClass, results)
        results.print_errors()
        results.print_sum_up()


class expect:
    class to_raise:
        def __init__(self, expected_exc):
            self.expected_exc = expected_exc

        def __enter__(self):
            pass

        def __exit__(self, exc_type, exc_val, exc_tb):
            if not exc_type:
                raise AssertionError("expected exception %s"
                                     % self.expected_exc.__name__)
            return True

    def __init__(self, context):
        self._context = context
        self._expected_exception = None

    @property
    def ok(self):
        """expect(a).ok"""
        assert self._context, \
            "expected %s, given %s" % (True, self._context)

    @property
    def not_ok(self):
        """expect(a).not_ok"""
        assert not self._context, \
            "expected not %s, given %s" % (True, self._context)

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

    def isinstance(self, expectation):
        assert isinstance(self._context, expectation), \
            "expected %s, given %s" % (expectation, type(self._context))

    def not_isinstance(self, expectation):
        assert not isinstance(self._context, expectation), \
            "expected not %s, given %s" % (expectation, type(self._context))

    def be_in(self, expectation):
        assert self._context in expectation, \
            "%s not in %s" % (self._context, expectation)

    def not_be_in(self, expectation):
        assert self._context not in expectation, \
            "%s in %s" % (self._context, expectation)

    def be(self, expectation):
        assert self._context is expectation, \
            "%s is not %s" % (self._context, expectation)

    def not_be(self, expectation):
        assert self._context is not expectation, \
            "%s is %s" % (self._context, expectation)

    @property
    def called(self):
        assert self._context.called

    @property
    def not_called(self):
        assert not self._context.called

    def called_with(self, *args, **kwargs):
        self._context.assert_any_call(*args, **kwargs)
