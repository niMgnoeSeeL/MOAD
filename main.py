from dm.program_space import ProgramSpace
from dm.factor.factor import get_factor_manager
from dm.response_manager import ResponseManager
from dm.doe.doe import get_doe_manager
from dm.log import create_root_logger, add_outputpath_log_handler
import argparse
import logging
import os

create_root_logger()
root_logger = logging.getLogger()


def get_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-p', '--proj_name', help='Target project name', required=True)
    parser.add_argument(
        '-f', '--factor_level', help='Factor level',
        choices=['line', 'srcml'],
        default='line')
    parser.add_argument(
        '-d', '--doe_strategy', help='Design of experiment strategy',
        choices=['onehot', 'random', 'nhot', 'ff2l',
                 '2hot', 'random_1000', 'random_2000'],
        default='onehot')
    parser.add_argument(
        '--doe_random_threshold', help='DoE random strategy threshold',
        type=float, default=0.0)
    parser.add_argument(
        '--max_n', help='Maximum combination for One2NHotDoE', type=int,
        default=0)
    parser.add_argument(
        '-i', '--max_expr', help='Maximum number of the experiment',
        default=100, type=int)
    parser.add_argument(
        '-o', '--output_name', help='Output(model) saving folder name',
        default=None)
    parser.add_argument(
        '--save_generated', help='Save all generated programs',
        action='store_true', default=False)
    parser.add_argument(
        '--save_log', help='Save log', action='store_true', default=False)
    parser.add_argument('--seed', help='Random seed', default=None)
    parser.add_argument('--planned_idx', help='Range of pre-planned idx, \
        from "start" to "end-1". If start == end, the range covers whole',
                        type=int, nargs=2, default=None)
    return parser


def main(args):
    root_logger.info('Create initial objects.')
    program_space = ProgramSpace(args.proj_name)
    program_space.base_work_dir = os.path.join(
        'output', 'experiment', args.proj_name, args.output_name)
    add_outputpath_log_handler(program_space.base_work_dir, root_logger)
    factor_manager = get_factor_manager(args.factor_level, args.proj_name,
                                        program_space)
    response_manager = ResponseManager(program_space)
    if args.planned_idx is None:
        plan_path, expr_idx_range = (None, None)
        iter_cnt = 0
    else:
        plan_path = os.path.join(program_space.base_work_dir, 'plan.csv')
        assert(os.path.exists(plan_path))
        if args.planned_idx[0] == args.planned_idx[1] == 0:
            expr_idx_range = 'all'
        else:
            expr_idx_range = range(args.planned_idx[0], args.planned_idx[1])
        iter_cnt = args.planned_idx[0]

    if args.doe_strategy == '2hot':
        args.doe_strategy = 'nhot'
        args.max_n = 2
    elif args.doe_strategy == 'random_1000':
        args.doe_strategy = 'random'
        args.max_expr = 1000
    elif args.doe_strategy == 'random_2000':
        args.doe_strategy = 'random'
        args.max_expr = 2000
    doe_manager = get_doe_manager(args.doe_strategy, factor_manager,
                                  response_manager, args.max_expr,
                                  args.doe_random_threshold, args.max_n,
                                  args.seed, plan_path, expr_idx_range)

    if args.planned_idx is None:
        root_logger.info('No plan exists. Save plan.')
        doe_manager.save_doe_plan(program_space)
        root_logger.info('Plan saved.')

    root_logger.info('Start iteration.')
    factor = doe_manager.get_next_factor()
    while factor is not None:
        root_logger.info(
            'Iter idx: {}, Qsize: {}'.format(iter_cnt, doe_manager.qsize))

        root_logger.info('Curr factor: {}'.format(factor))
        program_path = factor_manager.create_program(factor, iter_cnt,
                                                     args.save_generated)
        response = response_manager.get_response(program_path, args.save_log)
        root_logger.info('Response: {}'.format(response))
        doe_manager.append(factor, response)
        factor = doe_manager.get_next_factor()

        iter_cnt += 1

    root_logger.info('End iteration. Save model.')
    doe_manager.save_model(program_space)
    root_logger.info('Model saved. End program.')


if __name__ == "__main__":
    parser = get_parser()
    args = parser.parse_args()
    main(args)
