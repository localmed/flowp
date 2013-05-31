from flowp.testing import Behavior
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


class FlowpFileExecuter(Behavior):
    def before_each(self):
        self.args1 = ['script', 'task1', 'task2']
        self.args2 = ['script', 'task1:abc', 'task2']
        self.args3 = ['script', 'task1', 'task2:ab,cd']
        self.E = system.FlowpFileExecuter

    def it_parse_script_arguments_as_tasks_list_with_arguments(self):
        assert self.E(self.args1).tasks == {'task1': [], 'task2': []}
        assert self.E(self.args2).tasks == {'task1': ['abc'], 'task2': []}
        assert self.E(self.args3).tasks == {'task1': [], 'task2': ['ab', 'cd']}

    @mock.patch('flowp.system.import_alias')
    def it_executes_tasks_from_flowpfile_by_given_script_arguments(self, im_mock):
        flowpfile_mock = mock.MagicMock()
        im_mock.return_value = flowpfile_mock

        self.E(self.args1).execute()
        assert im_mock.call_args[0][0] == 'flowpfile'
        flowpfile_mock.task1.assert_called_with()
        flowpfile_mock.task2.assert_called_with()

        flowpfile_mock.reset_mock()
        self.E(self.args2).execute()
        flowpfile_mock.task1.assert_called_with('abc')
        flowpfile_mock.task2.assert_called_with()

        flowpfile_mock.reset_mock()
        self.E(self.args3).execute()
        flowpfile_mock.task1.assert_called_with()
        flowpfile_mock.task2.assert_called_with('ab', 'cd')
