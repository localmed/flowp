from flowp.testing import Behavior, expect, skip
from flowp import files
import os


class Cd(Behavior):
    def before_each(self):
        self.tmpdir.enter()
        os.mkdir('testdir')

    def after_each(self):
        self.tmpdir.exit()

    def it_changes_working_directory(self):
        files.cd('testdir')
        expect(os.getcwd().endswith('testdir')).to_be(True)

    def it_changes_working_directory_in_context(self):
        with files.cd('testdir'):
            expect(os.getcwd().endswith('testdir')).to_be(True)
        expect(os.getcwd().endswith('testdir')).to_be(False)


class Touch(Behavior):
    def before_each(self):
        self.tmpdir.enter()

    def after_each(self):
        self.tmpdir.exit()

    def it_creates_empty_file(self):
        expect(os.path.isfile('testfile')).to_be(False)
        files.touch('testfile')
        expect(os.path.isfile('testfile')).to_be(True)


class Mkdir(Behavior):
    def before_each(self):
        self.tmpdir.enter()

    def after_each(self):
        self.tmpdir.exit()

    def it_creates_empty_directory(self):
        expect(os.path.isdir('testdir')).to_be(False)
        files.mkdir('testdir')
        expect(os.path.isdir('testdir')).to_be(True)


@skip
class Cp(Behavior):
    def before_each(self):
        self.tmpdir.enter()

    def before_each(self):
        self.tmpdir.exit()

    class WhenFilenameInSourceGiven(Behavior):
        def it_test_something(self):
            pass
        pass

    class WhenGlobPatternInSourceGiven(Behavior):
        pass

    class WhenArrayOfFilenamesInSourceGiven(Behavior):
        pass

    class WhenArrayOfFilenamesAndGlobPatternsInSourceGiven(Behavior):
        pass


class Sh(Behavior):
    def it_executes_shell_commands(self):
        ccall = self.mock('subprocess.check_call')
        files.sh('test shell command')
        expect(ccall).to_have_been_called_with('test shell command', shell=True)
