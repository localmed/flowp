from flowp.testing import Behavior, when, expect, FileSystemBehavior
from flowp import system
from unittest import mock
import os


class FileUtilsInterface(FileSystemBehavior):
    def before_each(self):
        super().before_each()
        self.Subject = system.FileUtilsInterface

    def it_have_required_interface(self):
        self.Subject._cp
        self.Subject._mv
        self.Subject._ln
        self.Subject._rm


class System(FileSystemBehavior):
    def before_each(self):
        self.Subject = system
        super().before_each()

    def it_have_required_interface(self):
        self.Subject.cd
        self.Subject.cp
        self.Subject.mv
        self.Subject.ln
        self.Subject.pwd
        self.Subject.rm
        self.Subject.mkdir
        self.Subject.rmdir
        self.Subject.touch
        self.Subject.chmod
        self.Subject.chown


    @when('executes cp', 'path names given')
    def it_delegates_call_to_shutil_copy(self):
        with mock.patch('shutil.copy') as copy:
            system.cp('path1', 'path2')
            expect(copy).called_with('path1', 'path2')

    @when('executes cp', 'fileutilsinterface given')
    def it_uses_cp_interface_method(self):
        path = mock.Mock(spec=['_cp'])
        system.cp(path, 'string_path')
        expect(path._cp).called_with('string_path')
        system.cp('string_path2', path)
        expect(path._cp).called_with('string_path2')

    @when('executes mv', 'path names given')
    def it_delegates_call_to_shutil_move(self):
        with mock.patch('shutil.move') as move:
            system.mv('path1', 'path2')
            expect(move).called_with('path1', 'path2')

    @when('executes mv', 'fileutilsinterface given')
    def it_uses_mv_interface_method(self):
        path = mock.Mock(spec=['_mv'])
        system.mv(path, 'string_path')
        expect(path._mv).called_with('string_path')
        system.mv('string_path2', path)
        expect(path._mv).called_with('string_path2')

    @when('executes rm', 'path names given')
    def it_delegates_call_to_osunlink(self):
        with mock.patch('os.unlink') as rm:
            system.rm('path1')
            expect(rm).called_with('path1')

    @when('executes rm', 'fileutilsinterface given')
    def it_uses_rm_interface_method(self):
        path = mock.Mock(spec=['_rm'])
        system.rm(path)
        expect(path._rm).called

    def it_changes_working_directory(self):
        os.mkdir('testdir')
        system.cd('testdir')
        expect(os.getcwd().endswith('testdir')).ok

        # also act like a context manager
        self.reset_cwd()
        with system.cd('testdir'):
            expect(os.getcwd().endswith('testdir')).ok
        expect(os.getcwd().endswith('testdir')).not_ok

    def it_creates_empty_file(self):
        expect(os.path.isfile('testfile')).not_ok
        system.touch('testfile')
        expect(os.path.isfile('testfile')).ok

    def it_creates_directories(self):
        expect(os.path.isdir('testdir')).not_ok
        system.mkdir('testdir')
        expect(os.path.isdir('testdir')).ok
        expect(os.path.isdir('testdir/testdir2/testdir3')).not_ok
        system.mkdir('testdir/testdir2/testdir3')
        expect(os.path.isdir('testdir/testdir2/testdir3')).ok

    def it_moves_files(self):
        with open('testfile', 'w'):
            expect(os.path.isfile('testfile')).ok
            system.rm('testfile')
            expect(os.path.isfile('testfile')).not_ok

    @mock.patch('subprocess.check_call')
    def it_executes_shell_commands(self, subpr_mock):
        system.sh('test shell command')
        expect(subpr_mock).called_with('test shell command', shell=True)


class Path(FileUtilsInterface):
    def before_each(self):
        super().before_each()
        self.Subject = system.Path

    def it_have_required_interface(self):
        super().it_have_required_interface()
        self.Subject.is_directory
        self.Subject.is_exist   
        self.Subject.is_file
        self.Subject.is_readable
        self.Subject.is_writeable
        self.Subject.is_executable
        self.Subject.path
        self.Subject.absolute_path

    def it_checks_if_is_directory(self):
        system.touch('tmpfile')
        os.mkdir('tmpdir')
        expect(self.Subject('tmpfile').is_directory()).not_ok
        expect(self.Subject('tmpdir').is_directory()).ok

    def it_checks_if_is_exist(self):
        system.touch('tmpfile')
        os.mkdir('tmpdir')
        expect(self.Subject('tmpfile').is_exist()).ok
        expect(self.Subject('tmpdir').is_exist()).ok
        expect(self.Subject('ghost').is_exist()).not_ok



class File(Path):
    def before_each(self):
        super().before_each()
        self.Subject = system.File

    def it_have_required_interface(self):
        super().it_have_required_interface()
        self.Subject.read
        self.Subject.readline
        self.Subject.write
        self.Subject.size


class Directory(Path):
    def before_each(self):
        super().before_each()
        self.Subject = system.Directory

    def it_have_required_interface(self):
        super().it_have_required_interface()
        self.Subject.entries 


class Files(FileUtilsInterface):
    def before_each(self):
        super().before_each()
        self.Subject = system.Files

    def it_have_required_interface(self):
        super().it_have_required_interface()
        self.Subject.paths
        self.Subject.patterns


class Process(Behavior):
    def before_each(self):
        self.p = system.Process('testproc')

    def it_takes_basic_process_name_as_argument(self):
        pass

    def it_add_process_arguments(self):
        self.p.arg('--test1', 1)
        self.p.arg('--test2', ['a', 'b'])

    def it_generate_process_command_with_given_arguments_in_order(self):
        self.p.arg('--test1', 1)
        self.p.arg('--test2', ['a', 'b'])
        self.p.arg('test3')
        self.p.arg('t4', 't5')
        expect(self.p.command) == 'testproc --test1 1 --test2 a b test3 t4 t5'

    def it_update_arguments_values_without_changing_args_order(self):
        self.p.arg('-a', 1)
        self.p.arg('-b', 2)
        expect(self.p.command) == 'testproc -a 1 -b 2'
        self.p.arg('-a', 3)
        expect(self.p.command) == 'testproc -a 3 -b 2'

    @mock.patch('subprocess.check_call')
    def it_run_process(self, subpr_mock):
        self.p.arg('-a', 1)
        self.p.arg('b')
        expect(subpr_mock).not_called
        self.p.run()
        expect(subpr_mock).called
        subpr_mock.assert_called_once_with(['testproc', '-a', '1', 'b'])


class TermLogger(Behavior):
    def before_each(self):
        self.p1 = mock.patch('flowp.system.logging')
        self.logger_mock = mock.Mock()
        self.logging_mock = self.p1.start()
        self.logging_mock.getLogger.return_value = self.logger_mock
        self.logger = system.TermLogger()

    def after_each(self):
        self.p1.stop()
        

    def it_log_error_with_red_color(self):
        self.logger.error('msg')
        expect(self.logger_mock.error).called_with(system.TermLogger.RED + "msg" +
            system.TermLogger.COLOR_END)

    def it_log_info_with_regular_color(self):
        self.logger.info('msg')
        expect(self.logger_mock.info).called_with("msg")


class TaskScript(Behavior):
    def before_each(self):
        self.logger_mock = mock.Mock(spec=system.TermLogger)
        self.p1 = mock.patch('flowp.system.TermLogger',
                             new=mock.Mock(return_value=self.logger_mock))
        self.p1.start()

    def after_each(self):
        self.p1.stop()

    def executes_create(self):
        p1 = mock.patch('sys.argv', new=['task1', 'task2'])
        p2 = mock.patch('flowp.system.import_alias')
        p1.start()
        self.im_mock = p2.start()
        self.im_mock.side_effect = ImportError()
        yield
        p1.stop()
        p2.stop()

    def mocked_execute_tasks_method(self):
        p = mock.patch('flowp.system.TaskScript.execute_tasks')
        self.exc_mock = p.start()
        yield
        p.stop()

    @when(executes_create)
    def it_use_tasksfile_as_a_mixin_to_new_script_object(self):
        self.im_mock.side_effect = None
        class TestScript(system.TaskScript):
            t1 = None
            def task1(self):
                super().task1()
                self.t1 = True

        class TasksFile:
            t1b = None
            t2 = None
            def task1(self):
                self.t1b = True

            def task2(self):
                self.t2 = True

        tasksfile_mock = mock.MagicMock()
        tasksfile_mock.TasksFile = TasksFile
        self.im_mock.return_value = tasksfile_mock

        script = TestScript(['task1', 'task2']).create()

        expect(self.im_mock.call_args[0][0]) == 'tasksfile'
        expect(script.t1).ok
        expect(script.t1b).ok
        expect(script.t2).ok
   
    @when(executes_create, mocked_execute_tasks_method)
    def it_create_script_object_from_script_arguments(self):
        script = system.TaskScript.create()
        expect(script.argv) == ['task1', 'task2']

    @when(executes_create, mocked_execute_tasks_method)
    def it_ignore_importing_taskfile_if_not_founded(self):
        system.TaskScript.create()

    @when(executes_create, mocked_execute_tasks_method)
    def it_execute_tasks(self):
        expect(self.exc_mock).not_called
        script = system.TaskScript.create()
        expect(self.exc_mock).called

    def it_parse_given_arguments_to_tree_structure(self):
        expect(system.TaskScript(['task1', 'task2']).args) == \
            {'task1': [], 'task2': []}
        expect(system.TaskScript(['task1:abc', 'task2']).args) == \
            {'task1': ['abc'], 'task2': []}
        expect(system.TaskScript(['task1', 'task2:ab,cd']).args) == \
            {'task1': [], 'task2': ['ab', 'cd']}

    def it_executes_given_tasks_from_script(self):
        class TestScript(system.TaskScript):
            t1 = None
            t2 = None
            def task1(self):
                self.t1 = True

            def task2(self, a, b):
                self.t2 = [a,b] 

        script = TestScript(['task1', 'task2:1,2'])
        script.execute_tasks()
        expect(script.t1).ok
        expect(script.t2) == ['1','2']
        
    def it_log_executed_tasks(self):
        class TaskScript(system.TaskScript):
            def task1(self):
                pass
                
            def task2(self):
                pass 

        TaskScript(['task1']).execute_tasks()
        expect(self.logger_mock.info).called_with("Executing task task1")
