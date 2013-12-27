class Plugin:
    """
    Contains a group of task methods or other task plugins.
    """
    pass


class Script:
    """
    'task' script which can invoked from command line. It search
    plugins to raise a proper task method. Searching algorithm:

    #. taskfile.py in the current working directory (local)
    #. .task/plugins/ in the current working directory (local)
    #. $HOME/.task/plugins/ (global)
    """
    pass
