TaskScript
===============

Features:

    - task management
    - universal package management
    - scaffolding



Task file
-------------------

Example of taskfile.py:

    class TaskFile(system.TaskFile):
        def print_something(self):
            print("Tada!")


$ task print_something
Tada!



Task dependencies
-------------------

    class TaskFile(system.TaskFile):
        def t1(self):
            print('T1')

        @require(t1)
        def t2(self):
            print('T2')

        @require(t1, t2)
        def t3(self):
            print('T3')



$ task t3
T1
T2
T3

$ task t2
T1
T2


Task logger
-------------------

    from flowp import system
    import logging

    class TaskFile(system.TaskFile):
        logger = logging.getLogger('taskscript')

        def t1(self):
            pass

Custom task manager
---------------------

Example:

    #!/bin/env python

    from flowp import system

    class Foo(system.TaskScript):
        def install(self):
            print("Do installing!")

    Foo.parse()

$ foo install
Do installing!



Universal package management
-----------------------------

Package manager:

    class PackageManager(system.PackageManager):
        register = {
            'jquery2': Jquery2,
            'angularjs12': AngularJS12
        }

        def search(self):
            ...

        def list(self):
            ...


Package formula:

    class Jquery2(system.PackageFormula):
        source = 'git://something'
        require = []


Support for scaffolding
-------------------------


task install:scaffold


    from system import TaskFile, cp

    class TaskFile(system.TaskFile):
        tmpl = Template('/some/path/templates1')

        
        def genagnular(self, type):
            if type == 'controller':
                cp(self.tmpl('ctrl_pattern.js'), 'controller.js')
            


$ task genangular:controller
