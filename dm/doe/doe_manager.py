import os
import queue
import logging
import numpy as np
from abc import ABC, abstractmethod, ABCMeta

root_logger = logging.getLogger()


class DoEManager(ABC):
    __metaclass__ = ABCMeta

    @abstractmethod
    def __init__(
        self, factor_manager, response_manager, max_expr, plan_path, expr_idx_range=None,
    ):
        self._factor_size = factor_manager.size
        self._revise_factor = factor_manager.revise_factor
        if response_manager is None:
            self._response_size = -1
        else:
            self._response_size = response_manager.size
        self._matrix = {}
        self._max_expr = max_expr
        self._expr_cnt = 0
        self._factor_queue = queue.Queue()
        self._key_counter_dict = {}
        self._expr_idx_range = expr_idx_range

        # Debug
        root_logger.debug(
            "self._factor_size, self._response_size = {}, {}".format(
                self._factor_size, self._response_size
            )
        )

        self._init_factor_queue(plan_path, self._expr_idx_range)
        root_logger.info("Initial factor queue size: {}".format(self.qsize))

    @staticmethod
    def factor2key(factor):
        return "".join(list(map(str, factor)))

    @staticmethod
    def key2factor(key):
        return list(map(int, ",".join(key).split(",")))

    @staticmethod
    def response2numlist(response):
        return list(map(lambda x: 1 if x else 0, response))

    def append(self, factor, response):
        self._matrix[self.factor2key(factor)] = response

    @abstractmethod
    def _init_factor_queue(self, plan_path, expr_idx_range):
        plan = np.genfromtxt(plan_path, int, delimiter=",", skip_header=1)
        assert plan.shape[1] == self._factor_size
        if expr_idx_range == "all":
            self._expr_idx_range = expr_idx_range = range(0, len(plan))
        for factor in plan[expr_idx_range]:
            self.add_factor(factor)

    @property
    def qsize(self):
        return self._factor_queue.qsize()

    def add_factor(self, factor):
        revised_factor = self._revise_factor(factor)
        revised_key = self.factor2key(revised_factor)
        if revised_key not in self._key_counter_dict.keys():
            self._factor_queue.put(revised_factor)
            self._key_counter_dict[revised_key] = 1
        else:
            self._key_counter_dict[revised_key] += 1

    def get_next_factor(self):
        if self._expr_cnt < self._max_expr and not self._factor_queue.empty():
            self._expr_cnt += 1
            return self._factor_queue.get()
        else:
            return None

    def save_doe_plan(self, program_space):
        plan_path = os.path.join(program_space.base_work_dir, "plan.csv")
        root_logger.info("Saving plan(path: {}).".format(plan_path))
        plan = []
        while not self._factor_queue.empty():
            factor = self._factor_queue.get()
            key = self.factor2key(factor)
            plan.append([self._key_counter_dict[key]] + list(factor))
        for factor in plan:
            self._factor_queue.put(factor[1:])
        np_matrix = np.array(plan)
        np.savetxt(
            plan_path,
            np_matrix,
            delimiter=",",
            fmt="%d",
            header="cnt," + ",".join(["f{}".format(i) for i in range(self._factor_size)]),
        )

    def save_model(self, program_space):
        output_path = os.path.join(
            program_space.base_work_dir,
            "expr_{}_{}.csv".format(self._expr_idx_range.start, self._expr_idx_range.stop),
        )
        matrix = []
        for k, v in self._matrix.items():
            matrix.append(self.key2factor(k) + self.response2numlist(v))
        np_matrix = np.array(matrix)
        np.savetxt(
            output_path,
            np_matrix,
            delimiter=",",
            fmt="%d",
            header=",".join(["f{}".format(i) for i in range(self._factor_size)])
            + ",comp,"
            + ",".join(
                [
                    "c{}-{}".format(test_idx, crit_idx)
                    for test_idx in range(1, program_space.num_test + 1)
                    for crit_idx in range(1, program_space.num_crit + 1)
                ]
            ),
        )
