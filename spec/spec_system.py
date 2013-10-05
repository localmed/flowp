from flowp.testing import Behavior, when, expect
from flowp import system
from unittest import mock
import os
import shutil


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
        assert self.p.command == 'testproc --test1 1 --test2 a b test3 t4 t5'

    def it_update_arguments_values_without_changing_args_order(self):
        self.p.arg('-a', 1)
        self.p.arg('-b', 2)
        assert self.p.command == 'testproc -a 1 -b 2'
        self.p.arg('-a', 3)
        assert self.p.command == 'testproc -a 3 -b 2'

    @mock.patch('subprocess.check_call')
    def it_run_process(self, subpr_mock):
        self.p.arg('-a', 1)
        self.p.arg('b')
        assert not subpr_mock.called
        self.p.run()
        assert subpr_mock.called
        subpr_mock.assert_called_once_with(['testproc', '-a', '1', 'b'])


class FileUtils(Behavior):
    def before_each(self):
        self.org_working_dir = os.getcwd() 
        if os.path.isdir('spec/tmp'):
            shutil.rmtree('spec/tmp')
        os.mkdir('spec/tmp')
        os.chdir('spec/tmp')

    def after_each(self):
        os.chdir(self.org_working_dir) 
        shutil.rmtree('spec/tmp')

    def it_have_cd_function_which_enter_to_directories(self):
        os.mkdir('testdir')
        assert os.getcwd().endswith('tmp')
        system.cd('testdir')
        assert os.getcwd().endswith('tmp/testdir')

        # also act like a context manager
        os.chdir(self.org_working_dir + '/spec/tmp')
        assert os.getcwd().endswith('tmp')
        with system.cd('testdir'):
            assert os.getcwd().endswith('tmp/testdir')
        assert os.getcwd().endswith('tmp') 

    def it_have_mv_function_which_move_files(self):
        os.mkdir('testdir') 
        with open('testfile', 'w'):
            assert os.path.isfile('testfile') 
            assert not os.path.isfile('testdir/testfile') 
            system.mv('testfile', 'testdir/testfile')
            assert not os.path.isfile('testfile') 
            assert os.path.isfile('testdir/testfile') 

    def it_have_mkdir_function_which_creates_directory(self):
        assert not os.path.isdir('testdir')
        system.mkdir('testdir')
        assert os.path.isdir('testdir')
        assert not os.path.isdir('testdir/testdir2/testdir3')
        system.mkdir('testdir/testdir2/testdir3')
        assert os.path.isdir('testdir/testdir2/testdir3')

    def it_have_rm_function_which_remove_files(self):
        with open('testfile', 'w'):
            assert os.path.isfile('testfile')
            system.rm('testfile')
            assert not os.path.isfile('testfile')

    @mock.patch('subprocess.check_call')
    def it_have_sh_function_which_executes_shell_command(self, subpr_mock):
        system.sh('test shell command')
        subpr_mock.assert_called_once_with('test shell command', shell=True)


class Script(Behavior):
    def executes_parse(self):
        p1 = mock.patch('sys.argv', new=['task1', 'task2'])
        p2 = mock.patch('flowp.system.import_alias')
        p1.start()
        self.im_mock = p2.start()
        self.im_mock.side_effect = ImportError()
        yield
        p1.stop()
        p2.stop()

    def mocked_tasks_execution(self):
        p = mock.patch('flowp.system.Script.execute_tasks')
        self.exc_mock = p.start()
        yield
        p.stop()

    @when(executes_parse, mocked_tasks_execution)
    def it_create_script_object_with_script_arguments(self):
        script = system.Script.parse()
        expect(script.argv) == ['task1', 'task2']

    @when(executes_parse, mocked_tasks_execution)
    def it_pass_tasksfile_import_if_not_founded(self):
        system.Script.parse()

    @when(executes_parse)
    def it_use_tasksfile_as_a_mixin_to_new_script_object(self):
        self.im_mock.side_effect = None
        class TestScript(system.Script):
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

        script = TestScript(['task1', 'task2']).parse()

        expect(self.im_mock.call_args[0][0]) == 'tasksfile'
        expect(script.t1).ok
        expect(script.t1b).ok
        expect(script.t2).ok
   
    @when(executes_parse, mocked_tasks_execution)
    def it_execute_tasks(self):
        expect(self.exc_mock).not_called
        script = system.Script.parse()
        expect(self.exc_mock).called

    def it_parse_given_arguments_to_tree_structure(self):
        expect(system.Script(['task1', 'task2']).args) == \
            {'task1': [], 'task2': []}
        expect(system.Script(['task1:abc', 'task2']).args) == \
            {'task1': ['abc'], 'task2': []}
        expect(system.Script(['task1', 'task2:ab,cd']).args) == \
            {'task1': [], 'task2': ['ab', 'cd']}

    def it_executes_given_tasks_from_script(self):
        class TestScript(system.Script):
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
        


class SetupScript(Behavior):
    pass

class Task(Behavior):
    pass

class SetupTask(Behavior):
    pass
