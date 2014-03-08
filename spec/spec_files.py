from flowp.testing import Behavior, expect, skip
from flowp.files import cd, touch, mkdir, cp, sh, exists
import os


class Cd(Behavior):
    def before_each(self):
        self.tmpdir.enter()
        os.mkdir('testdir')

    def after_each(self):
        self.tmpdir.exit()

    def it_changes_working_directory(self):
        cd('testdir')
        expect(os.getcwd().endswith('testdir')).to_be(True)

    def it_changes_working_directory_in_context(self):
        with cd('testdir'):
            expect(os.getcwd().endswith('testdir')).to_be(True)
        expect(os.getcwd().endswith('testdir')).to_be(False)


class Touch(Behavior):
    def before_each(self):
        self.tmpdir.enter()

    def after_each(self):
        self.tmpdir.exit()

    def it_creates_empty_file(self):
        expect(os.path.isfile('testfile')).to_be(False)
        touch('testfile')
        expect(os.path.isfile('testfile')).to_be(True)


class Mkdir(Behavior):
    def before_each(self):
        self.tmpdir.enter()

    def after_each(self):
        self.tmpdir.exit()

    def it_creates_empty_directory(self):
        expect(os.path.isdir('testdir')).to_be(False)
        mkdir('testdir')
        expect(os.path.isdir('testdir')).to_be(True)


class Cp(Behavior):
    def before_each(self):
        self.tmpdir.enter()
        touch('file0.py')
        mkdir('testdir1')
        touch('testdir1/file1.py')
        touch('testdir1/file2.py')
        mkdir('testdir2')

    def after_each(self):
        self.tmpdir.exit()

    class WhenFilenameGiven(Behavior):
        def it_copy_single_file(self):
            cp('testdir1/file1.py', 'testdir2/file1b.py')
            expect(exists('testdir1/file1.py')).to_be(True)
            expect(exists('testdir2/file1b.py')).to_be(True)

    class WhenGlobPatternGiven(Behavior):
        def it_copy_group_of_files(self):
            cp('testdir1/*.py', 'testdir2')
            expect(exists('testdir2/file1.py')).to_be(True)
            expect(exists('testdir2/file2.py')).to_be(True)

    class WhenArrayOfFilenamesGiven(Behavior):
        def it_copy_group_of_files(self):
            cp(['testdir1/file1.py', 'testdir1/file2.py'], 'testdir2')
            expect(exists('testdir2/file1.py')).to_be(True)
            expect(exists('testdir2/file2.py')).to_be(True)

    class WhenArrayOfFilenamesAndGlobPatternsGiven(Behavior):
        def it_copy_group_of_files(self):
            cp(['file0.py', 'testdir1/*.py'], 'testdir2')
            expect(exists('testdir2/file0.py')).to_be(True)
            expect(exists('testdir2/file1.py')).to_be(True)
            expect(exists('testdir2/file2.py')).to_be(True)

    class WhenDirectoryGiven(Behavior):
        def it_copy_whole_directory(self):
            cp('testdir1', 'testdir3')
            expect(exists('testdir3/file1.py')).to_be(True)
            expect(exists('testdir3/file2.py')).to_be(True)



class Sh(Behavior):
    def it_executes_shell_commands(self):
        ccall = self.mock('subprocess.check_call')
        sh('test shell command')
        expect(ccall).to_have_been_called_with('test shell command', shell=True)
