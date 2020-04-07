import os
import shutil
import logging
from .factor_manager import FactorManager

root_logger = logging.getLogger()


class LineFactorManager(FactorManager):
    # todo: Handle ORBS log line on LineFactorManager, too
    def __init__(self, program_space):
        super().__init__(program_space)
        self._factor = []
        for filename in self._program_space.files:
            orig_filepath = os.path.join(program_space.orig_dir, filename)
            if not os.path.exists(orig_filepath):
                raise Exception("Invalid filepath: {}".format(orig_filepath))
            with open(orig_filepath) as f:
                self._factor += list(
                    map(lambda x: (filename, x), f.readlines()))
        self._size = len(self._factor)

        # Debug
        root_logger.debug('self._size = {}'.format(self._size))
        root_logger.debug('self._factor[0] = {}'.format(self._factor[0]))

    def create_program(self, factor, iter_cnt, save_flag, only_code=False):
        work_dir = super().create_program(factor, iter_cnt, save_flag,
                                          only_code)

        sliced_lines = list(
            map(lambda x: (x[1][0], '\n') if x[0] else x[1],
                tuple(zip(factor, self._factor))))

        for filename in self._program_space.files:
            filepath = os.path.join(work_dir, filename)
            if os.path.exists(filepath):
                os.remove(filepath)
            file_lines = list(
                map(lambda x: x[1], filter(lambda x: x[0] == filename, sliced_lines)))
            code = ''.join(file_lines)
            # Debug
            root_logger.debug('Filename:{} Code:\n{}'.format(filename, code))
            with open(os.path.join(work_dir, filepath), "w") as f:
                f.write(code)

        return work_dir

    @property
    def size(self):
        return self._size
