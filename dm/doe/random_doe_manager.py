import numpy as np
import logging
from .doe_manager import DoEManager

root_logger = logging.getLogger()


class RandomDoEManager(DoEManager):

    def __init__(self, factor_manager, response_manager, max_expr,
                 threshold, seed=None, plan_path=None, expr_idx_range=None):
        self._threshold = threshold
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
            while self.qsize < self._max_expr:
                sample = np.random.uniform(size=self._factor_size)
                self.add_factor((sample < self._threshold).astype(int))
            self._expr_idx_range = range(self.qsize)
