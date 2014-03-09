from flowp.testing import Behavior, skip
from flowp.files import cd, touch, mkdir, cp, sh, exists, isfile, isdir, pwd, Watch
from flowp import testing
import os


class expect(testing.expect):
    def to_be_file(self):
        assert isfile(self._context)

    def to_be_dir(self):
        assert isdir(self._context)

    def not_exists(self):
        assert not exists(self._context)


class Cd(Behavior):
    def before_each(self):
        self.tmpdir.enter()
        os.mkdir('testdir')

    def after_each(self):
        self.tmpdir.exit()

    def it_changes_working_directory(self):
        cd('testdir')
        expect(pwd().endswith('testdir')).to_be(True)

    def it_changes_working_directory_in_context(self):
        with cd('testdir'):
            expect(pwd().endswith('testdir')).to_be(True)
        expect(pwd().endswith('testdir')).to_be(False)


class Touch(Behavior):
    def before_each(self):
        self.tmpdir.enter()

    def after_each(self):
        self.tmpdir.exit()

    def it_creates_empty_file(self):
        expect('testfile').not_exists()
        touch('testfile')
        expect('testfile').to_be_file()


class Mkdir(Behavior):
    def before_each(self):
        self.tmpdir.enter()

    def after_each(self):
        self.tmpdir.exit()

    def it_creates_empty_directory(self):
        mkdir('testdir')
        expect('testdir').to_be_dir()

    class WhenPOptionGiven(Behavior):
        def it_creates_directories_recursivly(self):
            mkdir('td1/td2', p=True)


class FilesBehavior(Behavior):
    def before_each(self):
        self.tmpdir.enter()
        touch('file0.py')
        mkdir('testdir1')
        touch('testdir1/file1.py')
        touch('testdir1/file2.py')
        mkdir('testdir2')

    def after_each(self):
        self.tmpdir.exit()


class Cp(FilesBehavior):
    def it_copy_single_file(self):
        cp('testdir1/file1.py', 'testdir2/file1b.py')
        expect('testdir1/file1.py').to_be_file()
        expect('testdir2/file1b.py').to_be_file()

    def it_copy_group_of_files_by_glob_pattern(self):
        cp('testdir1/*.py', 'testdir2')
        expect('testdir2/file1.py').to_be_file()
        expect('testdir2/file2.py').to_be_file()

    def it_copy_group_of_files_by_file_names_list(self):
        cp(['testdir1/file1.py', 'testdir1/file2.py'], 'testdir2')
        expect('testdir2/file1.py').to_be_file()
        expect('testdir2/file2.py').to_be_file()

    def it_copy_whole_directory(self):
        cp('testdir1', 'testdir3')
        expect('testdir3/file1.py').to_be_file()
        expect('testdir3/file2.py').to_be_file()


class WatchClass(FilesBehavior):
    def before_each(self):
        super().before_each()
        self.filename = False
        self.event = None

        def callback(filename, event):
            self.filename = filename
            self.event = event

        self.callback = callback

    def it_monitor_files_changes(self):
        wp = Watch('testdir1/*.py', self.callback)
        expect(self.filename).to_be(False)
        with open('testdir1/file2.py', 'w') as f:
            f.write('test')
        wp.stop_when(lambda: self.filename, 1)
        expect(self.filename) == 'testdir1/file2.py'
        expect(self.event) == Watch.CHANGE
        expect(wp.is_alive()).to_be(False)

    @skip
    def it_monitor_new_files(self):
        wp = Watch('testdir1/*.py', self.callback)
        expect(self.filename).to_be(False)
        touch('testdir1/file3.py')
        wp.stop_when(lambda: self.event, 1)
        expect(self.filename) == 'testdir1/file2.py'
        expect(self.event) == Watch.NEW
        expect(wp.is_alive()).to_be(False)


class Sh(Behavior):
    def it_executes_shell_commands(self):
        ccall = self.mock('subprocess.check_call')
        sh('test shell command')
        expect(ccall).to_have_been_called_with('test shell command', shell=True)
