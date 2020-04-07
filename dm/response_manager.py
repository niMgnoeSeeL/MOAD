from .util import run, run_output
import logging

root_logger = logging.getLogger()


class ResponseManager:
    def __init__(self, program_space):
        self._base_work_dir = program_space.base_work_dir
        self._compile_script = program_space.compile_script
        self._execute_script = program_space.execute_script
        self._terminate_script = program_space.terminate_script
        self._num_test = program_space.num_test
        self._num_crit = program_space.num_crit

        # Debug
        root_logger.debug(
            "self._compile_script = {}".format(self._compile_script)
        )

    def get_response(self, program_path, save_log):
        comp_succ = False
        test_succ = []

        comp_result = run(self._compile_script, program_path)
        comp_succ = False if comp_result is None else True

        if comp_succ:
            exec_result = (
                run_output(self._execute_script, program_path)
                .rstrip()
                .split("\n")[-1]
            )
            if "2" in exec_result:
                raise Exception(
                    "Grep returned '2'; exec_result: {}".format(exec_result)
                )
            else:
                test_succ = list(
                    map(
                        lambda x: not (bool(int(x))),
                        list(exec_result.rstrip()),
                    )
                )
        else:
            test_succ = [False] * self._num_test * self._num_crit

        if not save_log:
            run(self._terminate_script, program_path)

        return [comp_succ] + test_succ

    @property
    def size(self):
        return 1 + self._num_test * self._num_crit
