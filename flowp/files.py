import os
import subprocess
import shutil
import glob as orgglob
import os.path
import threading
import time


# Aliases
exists = os.path.exists


def ls(path='.'):
    """Return a list of file names from given path."""
    return os.listdir(path)


def pwd():
    """Return current working directory"""
    return os.getcwd()


def chdir(path):
    """Change the current working directory to the specified path."""
    os.chdir(path)

isfile = os.path.isfile

isdir = os.path.isdir

islink = os.path.islink


def glob(pathname):
    """Return a list of paths matching a pathname pattern."""
    return orgglob.glob(pathname)


def rm(path, r=False):
    """Remove a file or whole directory if
    r=True argument given.
    """
    os.remove(path)


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


def touch(path):
    """Create an empty file"""
    with open(path, 'w'):
        pass


def mkdir(path, p=False):
    """Create an empty directory

    :param p:
        if true given it creates recursively directories
        from path
    """
    if p:
        os.makedirs(path)
    else:
        os.mkdir(path)


def sh(command):
    """Executes shell command as is"""
    subprocess.check_call(command, shell=True)


def cp(src, dst, r=False):
    """
    Copy files or directories if r=True argument given
    ::

        cp('dir/file.py', 'dir2/file.py')
        cp('dir/*.py', 'dir2')
        cp(['file1.py', 'file2.py'], 'dir')
        cp('dir1', 'dir2', r=True)

    """
    if isinstance(src, str):
        src = glob(src)

    for f in src:
        if os.path.isdir(f):
            if not r:
                raise IsADirectoryError("Is directory %s" % f)
            shutil.copytree(f, dst)
        else:
            shutil.copy(f, dst)


def mv(src, dst):
    """
    Move files or directories
    ::

        mv('dir/file.py', 'dir2/file.py')
        mv('dir/*.py', 'dir2')
        mv(['file1.py', 'file2.py'], 'dir')
        mv('dir1', 'dir2')

    """
    if isinstance(src, str):
        src = glob(src)

    for f in src:
        shutil.move(f, dst)


class Watch(threading.Thread):
    """Create and start watch thread that will watch
    files and call given callable if some of the
    watch actions occurs.

    :param files:
        files to watch given as glob path or list
        of files

    :param callback:
        callable(filename, action)

    ::

        def callback(filename, action):
            if action == Watch.CHANGE:
                ...

        w = Watch('*.py', callback)
        w.wait()

    """
    #: New file action
    NEW = 1
    #: File changed action
    CHANGE = 2
    #: File removed action
    DELETE = 3

    def __init__(self, files, callback):
        self._stopit = False
        self._files_registered = False
        super().__init__(target=self.loop, args=(files, callback))
        self.start()

    def stop(self, timeout=None):
        """Stop watch process. If timeout given stop
        process after given time.
        """
        if timeout:
            self.join(timeout)
        self._stopit = True
        self.join()

    def stop_when(self, predicate, timeout=None):
        """Stop watch process when callable predicate()
        evaluates to True. If timeout given stop
        process after given time.
        """
        if timeout:
            start_time = time.time()
        while not predicate():
            if timeout and (time.time() - start_time) > timeout:
                break
        self.stop()

    def wait_for_files_registered(self):
        while not self._files_registered:
            pass

    def wait(self):
        """Hold process in the waiting state,
        keep watcher running
        """
        try:
            self.join()
        except KeyboardInterrupt:
            self.stop()

    def loop(self, files_pattern, callback):
        files_sizes = {}

        if isinstance(files_pattern, str):
            files = glob(files_pattern)
        else:
            files = files_pattern

        for fn in files:
            files_sizes[fn] = os.path.getsize(fn)

        self._files_registered = True

        while True:
            if self._stopit:
                break

            if isinstance(files_pattern, str):
                files = glob(files_pattern)

            for fn in files:
                if self._stopit:
                    break
                if fn in files_sizes:
                    try:
                        if os.path.getsize(fn) != files_sizes[fn]:
                            callback(fn, self.CHANGE)
                            files_sizes[fn] = os.path.getsize(fn)
                    except FileNotFoundError:
                        callback(fn, self.DELETE)
                        del files_sizes[fn]
                else:
                    files_sizes[fn] = os.path.getsize(fn)
                    callback(fn, self.NEW)
