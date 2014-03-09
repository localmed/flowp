import os
import subprocess
import shutil
import glob as orgglob
import os.path
import threading
import time


# Aliases
exists = os.path.exists

ls = os.listdir

pwd = os.getcwd

chdir = os.chdir

isfile = os.path.isfile

isdir = os.path.isdir

islink = os.path.islink

glob = orgglob.glob


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


def mkdir(dirname, p=False):
    """Create an empty directory or directories recursivly
    if p option given.
    """
    if p:
        os.makedirs(dirname)
    else:
        os.mkdir(dirname)


def sh(command):
    """Executes shell command as is"""
    subprocess.check_call(command, shell=True)


def cp(src, dst):
    """Copy files and directories::

        cp('dir/file.py', 'dir2/file.py')
        cp('dir/*.py', 'dir2')
        cp(['file1.py', 'file2.py'], 'dir')
        cp('dir1', 'dir2')
    """
    if '*' in src:
        src = glob(src)

    if isinstance(src, list):
        for f in src:
            if os.path.isdir(f):
                shutil.copytree(f, dst)
            else:
                shutil.copy(f, dst)
    else:
        if os.path.isdir(src):
            shutil.copytree(src, dst)
        else:
            shutil.copy(src, dst)


class Watch(threading.Thread):
    NEW = 1
    CHANGE = 2
    DELETE = 3

    def __init__(self, files, callback):
        self._stopit = False
        super().__init__(target=self.loop, args=(self._list(files), callback))
        self.start()

    def _list(self, files):
        if '*' in files:
            files = glob(files)

        if isinstance(files, str):
            files = [files]

        if isinstance(files, list):
            return files
        return []

    def stop(self, timeout=None):
        if timeout:
            self.join(timeout)
        self._stopit = True
        self.join()

    def stop_when(self, predicate, timeout=None):
        if timeout:
            start_time = time.time()
        while not predicate():
            if timeout and (time.time() - start_time) > timeout:
                break
        self.stop()

    def loop(self, files, callback):
        files_sizes = {}
        while True:
            if self._stopit:
                break
            for fn in files:
                if self._stopit:
                    break
                if fn in files_sizes:
                    if os.path.getsize(fn) != files_sizes[fn]:
                        callback(fn, self.CHANGE)
                else:
                    files_sizes[fn] = os.path.getsize(fn)
