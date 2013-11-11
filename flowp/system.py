from flowp import ftypes
import subprocess
import os
import shutil
import sys
import logging


class FileUtilsInterface(ftypes.Object):
    def _cp(self):
        pass
    
    def _mv(self):
        pass

    def _ln(self):
        pass

    def _rm(self):
        pass


class Path(FileUtilsInterface):
    def __init__(self, value):
        self.value = value

    def is_directory(self):
        return os.path.isdir(self.value)

    def is_exist(self):
        return os.access(self.value, os.F_OK)

    def is_file(self):
        pass

    def is_readable(self):
        pass

    def is_writeable(self):
        pass

    def is_executable(self):
        pass

    def path(self):
        pass

    def absolute_path(self):
        pass


class File(Path):
    def read(self):
        pass

    def readline(self):
        pass

    def write(self):
        pass

    def size(self):
        pass


class Directory(Path):
    def entries(self):
        pass


class Files(FileUtilsInterface):
    def paths(self):
        pass

    def patterns(self):
        pass


class Process(ftypes.Object):
    """Manage structure of process / command
    Example:
        
        p = Process('./some/script')
        p.arg('--test1', 1)
        p.arg('--test2', ['a', 'b'])
        p.arg('test3')
        p.command # -> ./some/script --test1 1 --test2 a b test3
        p.run()
    """
    def __init__(self, process_name):
        """Create base of command structure as list"""
        self.elements = ftypes.List([process_name])

    def arg(self, kv, v=None):
        """Add arguments to the process
        :param kv:
            argument key/name or value right away
        :param v:
            argument value. It can be list/tuple or
            single value object.
        """
        def func(item):
            if item.isinstance(tuple) and item.len and item[0] == kv:
                return (kv, v)
            else:
                return item

        if v:
            if self.elements.filter(
                    lambda el: el.isinstance(tuple) and el[0] == kv):
                self.elements.map_it(func)
            else:
                self.elements.append((kv, v))
        else:
            self.elements.append(kv) 

    @property
    def command(self):
        """Return constructed command as string
        :rtype str:
        """
        return self.elements.flatten.flatten.join(' ')

    def run(self):
        """Run constructed command as process"""
        def func(item):
            if item.isinstance(str):
                return item
            else:
                return item.str

        subprocess.check_call(self.elements.flatten.map(func))


class cd:
    """Change working directory. Behave exacly like os.chdir, except
    that it can be used as context manager.
    Example:

        with cd('some/path'):
            # do some operations
            pass

    After exiting the context, return to the oryginal working directory.
    This also works but doesn't return to the original working dir:

        cd('some/path')
    """
    def __init__(self, path):
        self.org_dir = os.getcwd()
        os.chdir(path) 

    def __enter__(self):
        pass

    def __exit__(self, exc_type, exc_value, exc_traceback):
        os.chdir(self.org_dir)


# Alias for os.mkdir
mkdir = os.makedirs


# Alias for copy
def cp(src, dst):
    if hasattr(src, '_cp'):
        src._cp(dst)
    elif hasattr(dst, '_cp'):
        dst._cp(src)
    else:
        shutil.copy(src, dst)

# Alias for move
def mv(src, dst):
    if hasattr(src, '_mv'):
        src._mv(dst)
    elif hasattr(dst, '_mv'):
        dst._mv(src)
    else:
        shutil.move(src, dst)

def rm(path):
    if hasattr(path, '_rm'):
        path._rm()
    else:
        os.unlink(path)

def sh(command):
    """Executes shell command as is
    :param str command:
        command to execute
    """ 
    subprocess.check_call(command, shell=True)

def pwd():
    pass

def rmdir():
    pass

def touch(filename):
    with open(filename, 'w'):
        pass

def chmod():
    pass

def chown():
    pass

def ln():
    pass


# Import alias for better debugging / mocking
import_alias = __import__


class TermColors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    END = '\033[0m'


class TermLogger(ftypes.Object):
    GREEN = '\033[92m'
    RED = '\033[91m'
    COLOR_END = '\033[0m'
    
    def __init__(self):
        formatter = logging.Formatter('%(message)s')
        handler = logging.StreamHandler()
        handler.setLevel(logging.DEBUG)
        handler.setFormatter(formatter)
        self._logger = logging.getLogger()
        self._logger.setLevel(logging.DEBUG)
        self._logger.addHandler(handler)

    def error(self, msg):
        self._logger.error(self.RED + msg + self.COLOR_END)

    def info(self, msg):
        self._logger.info(msg)


# task2 = require(task1)(task2)
def require(*objects):
    """Set to method require property and put there require decorator objects"""
    def decorator(method):
        method.require = set(objects)
        return method
    return decorator


class TaskScript(ftypes.Object):
    @classmethod
    def create(cls):
        try:
            tasksfile = import_alias('tasksfile', globals(), locals(), [], -1) 
        except ImportError:
            script = cls(sys.argv)
        else:
            class FinalScript(cls, tasksfile.TasksFile):
                pass
            script = FinalScript(sys.argv)

        script.execute_tasks()
        return script

    def __init__(self, argv):
        self.argv = argv
        self.logger = TermLogger()

    @property
    def args(self):
        def func(item):
            if item.len == 1:
                return [item[0], []]
            else:
                return [item[0], item[1].split(',')]

        args = ftypes.List(self.argv)
        args.map_it(lambda x: x.split(':'))
        args.map_it(func)
        return args.dict

    def execute_tasks(self):
        for task, args in self.args.items():
            self.logger.info("Executing task %s" % task)
            self.getattr(task)(*args) 
