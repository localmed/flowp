from flowp.testing import Behavior, FilesBehavior, expect
from flowp import files
import os


class Cd(FilesBehavior):
    def before_each(self):
        super().before_each()
        os.mkdir('testdir')

    def it_changes_working_directory(self):
        files.cd('testdir')
        expect(os.getcwd().endswith('testdir')).to_be(True)

    def it_changes_working_directory_in_context(self):
        with files.cd('testdir'):
            expect(os.getcwd().endswith('testdir')).to_be(True)
        expect(os.getcwd().endswith('testdir')).to_be(False)


class Touch(FilesBehavior):
    def it_creates_empty_file(self):
        expect(os.path.isfile('testfile')).to_be(False)
        files.touch('testfile')
        expect(os.path.isfile('testfile')).to_be(True)


class Sh(Behavior):
    def it_executes_shell_commands(self):
        ccall = self.mock('subprocess.check_call')
        files.sh('test shell command')
        expect(ccall).to_have_been_called_with('test shell command', shell=True)
