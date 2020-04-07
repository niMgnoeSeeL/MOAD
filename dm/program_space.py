import os
import logging
from .config import Config


root_logger = logging.getLogger()


class ProgramSpace:
    def __init__(self, proj_name):
        self._proj_name = proj_name
        self._proj_path = os.path.join("output", "original", proj_name)
        self._config = Config(os.path.join(self._proj_path, "config", "config.ini"))
        self._orig_dir = os.path.join(
            self._proj_path, self._config.getstr("PROGRAMSPACE", "orig_dir")
        )
        self._files = self._config.getlist("PROGRAMSPACE", "files")
        self._script_dir = os.path.join(
            self._proj_path, self._config.getstr("SCRIPT", "script_dir")
        )
        self._compile_script = self._config.getstr("SCRIPT", "compile_script")
        self._execute_script = self._config.getstr("SCRIPT", "execute_script")
        self._terminate_script = self._config.getstr("SCRIPT", "terminate_script")
        self._num_test = self.get_num_test()
        self._num_crit = self.get_num_crit()

    @property
    def orig_dir(self):
        return self._orig_dir

    @property
    def files(self):
        return self._files

    @property
    def compile_script(self):
        return os.path.join(self._script_dir, self._compile_script)

    @property
    def execute_script(self):
        return os.path.join(self._script_dir, self._execute_script)

    @property
    def terminate_script(self):
        return os.path.join(self._script_dir, self._terminate_script)

    @property
    def num_test(self):
        return self._num_test

    @property
    def num_crit(self):
        return self._num_crit

    @property
    def proj_path(self):
        return self._proj_path

    @property
    def proj_name(self):
        return self._proj_name

    @property
    def base_work_dir(self):
        return self._base_work_dir

    @base_work_dir.setter
    def base_work_dir(self, path):
        self._base_work_dir = path
        os.makedirs(self._base_work_dir, exist_ok=True)

    def get_num_test(self):
        return len(os.listdir(os.path.join(self._script_dir, "testsuite")))

    def get_num_crit(self):
        with open(os.path.join(self._script_dir, "criteria")) as f:
            return len(f.readlines())
