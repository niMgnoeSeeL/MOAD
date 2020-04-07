import numpy as np
import logging
from .doe_manager import DoEManager

root_logger = logging.getLogger()


class FF2LDoEManager(DoEManager):

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
            power2 = 2
            factor_idx = 1
            factor_list = np.array([[True], [False]])
            while factor_idx < self._factor_size:
                factor_idx += 1
                if factor_idx == power2:
                    factor_list = np.hstack((
                        np.vstack((factor_list, np.logical_not(factor_list))),
                        np.array([[True] * power2 + [False] * power2]).reshape(power2 * 2, 1)))
                    power2 *= 2
                else:
                    lhs_idx = factor_idx - int(power2 / 2) - 1
                    rhs_idx = int(power2 / 2) - 1
                    new_col = np.logical_xor(factor_list[:, lhs_idx], factor_list[:, rhs_idx])
                    factor_list = np.hstack((factor_list, new_col.reshape(power2, 1)))

            # np.random.shuffle(factor_list)
            for factor in factor_list:
                self.add_factor(factor.astype(int).tolist())
            self._expr_idx_range = range(self.qsize)
