from flowp.testing import Behavior
from flowp import doo


class Script(Behavior):
    def before_each(self):
        self.imp = self.mock('importlib.import_module')

    def it_parse_argv_list(self):
        pass

    def it_run_proper_tasks_from_taskfile(self):
        pass