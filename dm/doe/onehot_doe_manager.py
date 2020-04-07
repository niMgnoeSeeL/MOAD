import logging
import numpy as np
from .doe_manager import DoEManager

root_logger = logging.getLogger()


class OneHotDoEManager(DoEManager):

    def __init__(self, factor_manager, response_manager, max_expr, seed=None,
                 plan_path=None, expr_idx_range=None):
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
            # empty_pos_list = np.random.permutation(self._factor_size)
            empty_pos_list = list(range(self._factor_size))
            factor_list = list(map(lambda empty_pos:
                                   list(map(lambda pos:
                                            1 if pos == empty_pos else 0,
                                            range(self._factor_size))),
                                   empty_pos_list))
            for factor in factor_list:
                self.add_factor(factor)
            self._expr_idx_range = range(self.qsize)