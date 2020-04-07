import os
import numpy as np
import argparse
import logging
import glob
from dm.program_space import ProgramSpace
from dm.factor.factor import get_factor_manager
from dm.response_manager import ResponseManager
from dm.log import add_outputpath_log_handler

from sklearn.linear_model import LogisticRegression

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


# proj path
# output path default: /tmp/dm_temp
# data path


def get_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-p", "--proj_name", help="Target project path", required=True
    )
    parser.add_argument(
        "-d", "--data_name", help="Data dir name", required=True
    )
    parser.add_argument(
        "-i",
        "--inference",
        help="Inference algorithm",
        choices=["once_success", "logistic", "simple_bayes"],
        required=True,
    )
    parser.add_argument(
        "--save_generated",
        help="Save all generated programs",
        action="store_true",
        default=False,
    )
    parser.add_argument(
        "--save_log", help="Save log", action="store_true", default=False
    )
    parser.add_argument(
        "--sub_sample",
        help="Use only portion of the samples. [0.0 - 1.0]",
        type=float,
        default=1.0,
    )
    parser.add_argument(
        "--output_path",
        help="Explicitly state out the output path",
        default=None,
    )
    parser.add_argument(
        "--seed", type=int, help="Numpy random seed", default=None
    )
    return parser


def get_criteria(proj_name):
    proj_path = os.path.join("output", "original", proj_name)
    criteria_path = os.path.join(proj_path, "scripts/criteria")
    if os.path.exists(criteria_path):
        with open(criteria_path) as f:
            logger.info("Criteria path loaded (path:{})".format(criteria_path))
            return list(map(str.rstrip, f.readlines()))
    else:
        logger.info("No criteria path exists.")


def row2str(data) -> str:
    return " ".join(data.astype(int).astype(str))


def get_factor(data, factor_size) -> np.ndarray:
    np_data = np.array(data)
    if data.ndim == 1:
        return np_data[:factor_size]
    else:
        return np_data[:, :factor_size]


def get_response(data, response_size) -> np.ndarray:
    np_data = np.array(data)
    if data.ndim == 1:
        return np_data[-response_size:]
    else:
        return np_data[:, -response_size:]


def get_factor_once_success(
    sample_data, factor_size, test_idx_list
) -> np.ndarray:
    test_succ_row_list = list(
        filter(
            lambda row: np.bitwise_and.reduce(row[test_idx_list], 0),
            sample_data,
        )
    )
    if len(test_succ_row_list) == 0:
        return np.array([False] * factor_size)
    else:
        return get_factor(
            np.bitwise_or.reduce(test_succ_row_list, 0), factor_size
        )


def getXy(sample_data, factor_size, test_idx_list) -> (np.ndarray, np.ndarray):
    return (
        sample_data[:, :factor_size],
        np.bitwise_and.reduce(sample_data[:, test_idx_list], 1),
    )


def get_factor_logistic_regression(
    sample_data, factor_size, test_idx_list
) -> np.ndarray:
    X, y = getXy(sample_data, factor_size, test_idx_list)
    if len(set(y)) == 1:
        if y[0]:
            return np.array([True] * factor_size)
        else:
            return np.array([False] * factor_size)
    clf = LogisticRegression(random_state=0, solver="lbfgs").fit(X, y)
    return np.array(list(map(lambda x: 1 if x > 0 else 0, clf.coef_[0])))


# p(Response=1|Factor=1) = p(Response=1 && Factor=1) / p(Factor=1)
def get_factor_individual_bayesian(
    sample_data, factor_size, test_idx_list
) -> np.ndarray:
    X, y = getXy(sample_data, factor_size, test_idx_list)
    factor_prop = []
    count_factor_1 = np.count_nonzero(X, axis=0)
    for factor_idx in range(len(X[0])):
        factor_col = X[:, factor_idx]
        count_factor_1_response_1 = np.count_nonzero(
            np.logical_and(factor_col, y)
        )
        assert count_factor_1_response_1 <= count_factor_1[factor_idx]
        factor_prop.append(
            count_factor_1_response_1 / count_factor_1[factor_idx]
        )
    logger.debug(
        ", ".join(list(map(lambda x: "{:.2f}".format(x), factor_prop)))
    )
    factor_prop = np.array(factor_prop)
    return factor_prop > np.mean(factor_prop)


def check_factor_sample(
    factor_manager, response_manager, factor, save_generated, save_log, raw_idx
) -> np.ndarray:
    program_path = factor_manager.create_program(
        factor, raw_idx, save_generated
    )
    return np.array(response_manager.get_response(program_path, save_log))


def get_data(data_dir_path, sub_sample: float):
    data_path_list = sorted(
        list(
            filter(
                lambda x: os.path.basename(x).startswith("expr"),
                glob.glob(os.path.join(data_dir_path, "*")),
            )
        )
    )
    logger.debug("data_path_list: {}".format(data_path_list))
    data_path = data_path_list[0]
    with open(data_path) as f:
        logger.info(f.readline().lstrip("# ").rstrip())
    data = np.genfromtxt(data_path, delimiter=",", skip_header=1).astype(bool)

    for data_path in data_path_list[1:]:
        with open(data_path) as f:
            logger.info(f.readline().lstrip("# ").rstrip())
        data = np.vstack(
            (
                data,
                np.genfromtxt(data_path, delimiter=",", skip_header=1).astype(
                    bool
                ),
            )
        )
    logger.info("expr_cnt: {}".format(len(data)))
    sample_size = int(len(data) * sub_sample)
    logger.info(
        "sub_sample: {}, sample_size: {}".format(sub_sample, sample_size)
    )
    data = data[np.random.choice(len(data), sample_size, replace=False), :]
    return data


def infer_factor(
    data,
    factor_manager,
    response_manager,
    num_test,
    num_crit,
    raw_idx,
    inference,
    criterion,
    save_generated,
    save_log,
):
    response_idx_list = np.array(range(num_test)) * num_crit + raw_idx + 1
    vector_idx_list = factor_manager.size + response_idx_list
    logger.info(
        "Criterion {} ({}): response_idx_list:{}, vector_idx_list:{}".format(
            criterion, raw_idx + 1, response_idx_list, vector_idx_list
        )
    )

    get_factor_func = None
    if inference == "once_success":
        get_factor_func = get_factor_once_success
    elif inference == "logistic":
        get_factor_func = get_factor_logistic_regression
    elif inference == "simple_bayes":
        get_factor_func = get_factor_individual_bayesian

    factor = get_factor_func(data, factor_manager.size, vector_idx_list)
    logger.info("inferred factor:\n{}".format(factor.astype(int)))

    response = check_factor_sample(
        factor_manager,
        response_manager,
        list(factor.astype(int)),
        save_generated,
        save_log,
        raw_idx + 1,
    )
    logger.info(
        "succ: {} ({})".format(
            np.bitwise_and.reduce(response[response_idx_list], 0),
            response[response_idx_list].astype(int),
        )
    )

    return np.bitwise_and.reduce(response[response_idx_list])


if __name__ == "__main__":
    parser = get_parser()
    args = parser.parse_args()

    if args.seed is not None:
        np.random.seed(args.seed)

    if args.output_path is None:
        output_path = os.path.join(
            "output", "model", args.proj_name, args.data_name, args.inference
        )
    else:
        output_path = args.output_path
    program_space = ProgramSpace(args.proj_name)
    program_space.base_work_dir = output_path
    add_outputpath_log_handler(output_path, logger)

    logger.info("output_path: {}".format(output_path))

    factor_manager = get_factor_manager("srcml", args.proj_name, program_space)
    response_manager = ResponseManager(program_space)
    data_dir_path = os.path.join(
        "output", "experiment", args.proj_name, args.data_name
    )
    data = get_data(data_dir_path, args.sub_sample)
    criteria_list = get_criteria(args.proj_name)

    assert (response_manager.size - 1) / program_space.num_test == len(
        criteria_list
    )

    data_response = get_response(data, response_manager.size)
    unique_response = set(list(map(row2str, data_response)))
    logger.info("unique response cnt: {}".format(len(unique_response)))
    for response in unique_response:
        logger.info(str(response))

    succ_list = []

    for i in range(len(criteria_list)):
        succ_list.append(
            infer_factor(
                data,
                factor_manager,
                response_manager,
                program_space.num_test,
                len(criteria_list),
                i,
                args.inference,
                criteria_list[i],
                args.save_generated,
                args.save_log,
            )
        )

    logger.info("success rate: {}".format(np.mean(succ_list)))
