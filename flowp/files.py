import os
import subprocess
import shutil
import glob
import os.path


class cd:
    """Change working directory. Behave exacly like os.chdir, except
    that it can be used as context manager.
    Example::

        with cd('some/path'):
            # do some operations
            pass

    After exiting the context, return to the oryginal working directory.
    This also works but doesn't return to the original working dir::

        cd('some/path')
    """
    def __init__(self, path):
        self.org_dir = os.getcwd()
        os.chdir(path)

    def __enter__(self):
        pass

    def __exit__(self, exc_type, exc_value, exc_traceback):
        os.chdir(self.org_dir)


def touch(filename):
    """Create an empty file"""
    with open(filename, 'w'):
        pass


def mkdir(dirname):
    """Create an empty directory"""
    os.mkdir(dirname)


def sh(command):
    """Executes shell command as is"""
    subprocess.check_call(command, shell=True)


exists = os.path.exists


def cp(src, dst):
    """Copy files and directories::

        cp('dir/file.py', 'dir2/file.py')
        cp('dir/*.py', 'dir2')
        cp(['file1.py', 'dir/*.py'], 'dir')
    """
    if '*' in src:
        src = glob.glob(src)

    if isinstance(src, list):
        for f in src:
            cp(f, dst)
    else:
        if os.path.isdir(src):
            shutil.copytree(src, dst)
        else:
            shutil.copy(src, dst)
