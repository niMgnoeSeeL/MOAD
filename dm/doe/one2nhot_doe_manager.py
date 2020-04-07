import logging
import itertools
import numpy as np
from .doe_manager import DoEManager

root_logger = logging.getLogger()


class One2NHotDoEManager(DoEManager):

    def __init__(self, factor_manager, response_manager, max_expr,
                 max_n, seed=None, plan_path=None, expr_idx_range=None):
        self._max_n = max_n
        self._factor_manager = factor_manager
        if seed:
            print('Numpy random seed: {}'.format(seed))
            root_logger.debug('Numpy random seed: {}'.format(seed))
            np.random.seed(int(seed))
        super().__init__(factor_manager, response_manager, max_expr,
                         plan_path, expr_idx_range)

    def _init_factor_queue(self, plan_path=None, expr_idx_range=None):
        if plan_path is not None and expr_idx_range is not None:
            super()._init_factor_queue(plan_path, expr_idx_range)
        else:
            self.add_factor([0] * self._factor_size)
            for i in range(self._max_n):
                empty_pos_list = itertools.combinations(range(self._factor_size), i + 1)
                factor_list = list(map(lambda empty_pos:
                                       list(map(lambda pos:
                                                1 if pos in empty_pos else 0,
                                                range(self._factor_size))),
                                       empty_pos_list))
                # np.random.shuffle(factor_list)
                for factor in factor_list:
                    if self._factor_manager.is_valid_factor(factor):
                        self.add_factor(factor)
                self._expr_idx_range = range(self.qsize)
