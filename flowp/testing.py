import unittest
import re


class BDDTestCase(type):
    def __new__(cls, name, bases, namespace, **kwargs):
        new_namespace = {}
        for key, value in namespace.items():
            if key == 'before_each':
                key = 'setUp'

            if key == 'after_each':
                key = 'tearDown'

            new_namespace[key] = value

        return type.__new__(cls, name, bases, new_namespace)


class Behavior(unittest.TestCase):
    __metaclass__ = BDDTestCase


class TestProgram(unittest.TestProgram):
    def _do_discovery(self, argv, Loader = None):
        """New _do_discovery method which takes into consideration 
            testLoader parameter from __init__ method"""
        if not Loader:
            Loader = type(self.testLoader)
        super(TestProgram, self)._do_discovery(argv, Loader)


class TestLoader(unittest.TestLoader):
    testMethodPrefix = 'it'

    def discover(self, start_dir, pattern='spec*.py', top_level_dir=None):
        # Force spec pattern
        pattern = 'spec*.py'
        return super(TestLoader, self).discover(start_dir, pattern, top_level_dir) 


class TextTestResult(unittest.TestResult):
    separator1 = '-' * 70
    separator2 = '-' * 70
    groups = set()
    COLOR_GREEN = '\033[92m'
    COLOR_RED = '\033[91m'
    COLOR_END = '\033[0m'
    COLOR_BLUE = '\033[94m'

    def __init__(self, stream, descriptions, verbosity):
        super(TextTestResult, self).__init__()
        self.stream = stream
        self.showAll = verbosity > 1
        self.dots = verbosity == 1
        self.descriptions = descriptions


    def getGroupDescription(self, test):
        return str(test).split()[1][1:-1]

    def getDescription(self, test):
        test_name = str(test).split()[0].replace('_', ' ')[3:]
        return test_name

    def getFormattedDescription(self, test):
        prefix = '    - '
        postfix = ' ... '
        description = self.getDescription(test)
        return prefix + description + postfix

    def startTest(self, test):
        super(TextTestResult, self).startTest(test)
        if self.showAll:
            group = self.getGroupDescription(test)
            if group not in self.groups:
                self.stream.writeln("\n%s:" % group)
                self.groups.add(group)

            self.stream.flush()

    def addSuccess(self, test):
        super(TextTestResult, self).addSuccess(test)
        if self.showAll:
            self.stream.write(self.COLOR_GREEN)
            self.stream.write(self.getFormattedDescription(test))
            self.stream.writeln("OK")
            self.stream.write(self.COLOR_END)
        elif self.dots:
            self.stream.write('.')
            self.stream.flush()

    def addError(self, test, err):
        super(TextTestResult, self).addError(test, err)
        if self.showAll:
            self.stream.write(self.COLOR_RED)
            self.stream.write(self.getFormattedDescription(test))
            self.stream.writeln("ERROR")
            self.stream.write(self.COLOR_END)
        elif self.dots:
            self.stream.write('E')
            self.stream.flush()

    def addFailure(self, test, err):
        super(TextTestResult, self).addFailure(test, err)
        if self.showAll:
            self.stream.write(self.COLOR_RED)
            self.stream.write(self.getFormattedDescription(test))
            self.stream.writeln("FAIL")
            self.stream.write(self.COLOR_END)
        elif self.dots:
            self.stream.write('F')
            self.stream.flush()

    def addSkip(self, test, reason):
        super(TextTestResult, self).addSkip(test, reason)
        if self.showAll:
            self.stream.write(self.getDescription(test))
            self.stream.writeln("skipped {0!r}".format(reason))
        elif self.dots:
            self.stream.write("s")
            self.stream.flush()

    def addExpectedFailure(self, test, err):
        super(TextTestResult, self).addExpectedFailure(test, err)
        if self.showAll:
            self.stream.write(self.getDescription(test))
            self.stream.writeln("expected failure")
        elif self.dots:
            self.stream.write("x")
            self.stream.flush()

    def addUnexpectedSuccess(self, test):
        super(TextTestResult, self).addUnexpectedSuccess(test)
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

    def _format_traceback_line(self, line):
        line = '  ' + line
        file_line = re.match(r'^\s*File "([\w/\.-]+)", line (\d+),', line)
        if file_line:
            return '    %s:%s' % (file_line.group(1), file_line.group(2))
        elif re.match(r'^Traceback', line):
            return ''
        elif re.match(r'^  \S', line):
            return self.COLOR_BLUE + line + self.COLOR_END
        else:
            return line

    def _format_traceback(self, traceback):
        if self.dots:
            traceback = traceback.split("\n")[1:]
            traceback = map(self._format_traceback_line, traceback)
            traceback = "\n".join(traceback)

        return traceback

    def printErrorList(self, flavour, errors):
        for test, err in errors:
            self.stream.writeln(self.separator1)
            self.stream.writeln()
            place = '"%s" [%s]' % (self.getDescription(test), self.getGroupDescription(test))
            self.stream.write(self.COLOR_RED)
            self.stream.writeln("%s: %s" % (flavour, place))
            self.stream.write(self.COLOR_END)
            self.stream.writeln()
            self.stream.writeln("%s" % self._format_traceback(err))


class TextTestRunner(unittest.TextTestRunner):
    resultclass = TextTestResult


main = TestProgram

if __name__ == '__main__':
    loader = TestLoader()
    main(testLoader=loader, testRunner=TextTestRunner)
