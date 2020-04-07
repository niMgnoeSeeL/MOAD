import os
import shutil
import logging
from abc import ABC, abstractmethod, ABCMeta

root_logger = logging.getLogger()


class FactorManager(ABC):
    __metaclass__ = ABCMeta

    @abstractmethod
    def __init__(self, program_space):
        self._program_space = program_space
        self._factor = None
        self._size = 0

    @abstractmethod
    def create_program(self, factor, iter_cnt, save_flag, only_code=False):
        work_dir = self.get_work_dir(iter_cnt, save_flag)
        if os.path.isdir(work_dir):
            shutil.rmtree(work_dir)
        if only_code:
            os.makedirs(work_dir)
            for filename in self._program_space.files:
                shutil.copy(
                    os.path.join(self._program_space.orig_dir, filename),
                    os.path.join(work_dir, filename),
                )
        else:
            work_dir = shutil.copytree(self._program_space.orig_dir, work_dir)
        with open(os.path.join(work_dir, "factor"), "w") as f:
            f.write(str(factor))
        return work_dir

    def get_work_dir(self, iter_cnt, save_flag):
        if save_flag:
            return os.path.join(self._program_space.base_work_dir, str(iter_cnt))
        else:
            return os.path.join(self._program_space.base_work_dir, "work")

    def revise_factor(self, factor):
        return factor

    def is_valid_factor(self, factor):
        return True

    @property
    def size(self):
        return self._size

    @property
    def factor(self):
        return self._factor

    @property
    def program_space(self):
        return self._program_space
