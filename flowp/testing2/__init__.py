import glob
import os.path
import re
import importlib
import sys
import inspect


class Behavior:
    """Test case"""
    parent_behavior = None

    def before_each(self):
        pass

    def after_each(self):
        pass


class Runner:
    """Parse script arguments and run tests"""
    test_method_prefix = 'it_'
    spec_file_prefix = 'spec_'
    behavior_cls = Behavior

    def __init__(self):
        pass

    def get_spec_modules(self):
        """Get modules to tests"""
        files = glob.glob('**/spec_*.py')
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

    def run_test_method(self, method_name, results, behavior_instance):
        method = getattr(behavior_instance, method_name)
        try:
            #self.run_before_each_methods(behavior_instance)
            method()
            #self.run_after_each_methods(behavior_instance)
        except:
            pass

    def run_behavior(self, behavior, results):
        for attr_name in dir(behavior):
            attr = getattr(behavior, attr_name)
            if self.is_test_function(attr):
                print("#2 Executing %s" % attr_name)
                behavior_instance = behavior()
                # Executing test method
                self.run_test_method(attr_name, results, behavior_instance)
            elif self.is_behavior_class(attr):
                attr.parent_behavior = behavior
                self.run_behavior(attr, results)

    def run(self):
        results = Results(None)
        for module in self.get_spec_modules():
            for BClass in self.get_behavior_classes(module):
                print('#1', BClass, module)
                self.run_behavior(BClass, results)


class Results:
    """Gather informations about test results"""
    def __init__(self, stream):
        self.stream = stream
        self.failures = []
        self.errors = []
        self.skipped = []
        self.runned_tests_count = 0

    def start_test(self):
        pass

    def stop_test(self):
        pass

    def add_success(self):
        pass

    def add_failure(self):
        pass

    def add_error(self):
        pass

    def print_errors(self):
        pass
