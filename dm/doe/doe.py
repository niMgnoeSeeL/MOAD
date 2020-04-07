import logging
from .onehot_doe_manager import OneHotDoEManager
from .random_doe_manager import RandomDoEManager
from .one2nhot_doe_manager import One2NHotDoEManager
from .fractional_factorial_doe_manager import FF2LDoEManager
# from .packett_burman_doe_manager import PackettBurmanDoEManager


root_logger = logging.getLogger()


def get_doe_manager(doe_strategy, factor_manager, response_manager, max_expr,
                    threshold=0.0, max_n=0, seed=None,
                    plan_path=None, expr_idx_range=None):
    if doe_strategy == 'onehot':
        return OneHotDoEManager(factor_manager, response_manager, max_expr,
                                seed, plan_path, expr_idx_range)
    elif doe_strategy == 'random':
        if threshold == 0.0:
            root_logger.info('Set default doe_random_threshold: 1 / ({}:factor_size) = {}'.format(
                factor_manager.size, 1 / factor_manager.size))
            threshold = 1 / factor_manager.size
        manager = RandomDoEManager(factor_manager, response_manager,
                                   max_expr, threshold, seed,
                                   plan_path, expr_idx_range)
        return manager
    elif doe_strategy == 'nhot':
        if max_n <= 0:
            raise Exception('Invalid max_n({})', format(max_n))
        else:
            return One2NHotDoEManager(factor_manager, response_manager,
                                      max_expr, max_n, seed,
                                      plan_path, expr_idx_range)
    elif doe_strategy == 'ff2l':
        return FF2LDoEManager(factor_manager, response_manager, max_expr,
                              seed, plan_path, expr_idx_range)
    else:
        raise Exception('Invalid factor_level: {}'.format(doe_strategy))
