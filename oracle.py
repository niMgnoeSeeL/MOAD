import os
import shutil
import argparse
from dm.config import Config
from dm.program_space import ProgramSpace
from dm.util import run


def get_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-p', '--proj_name', help='Target project name', required=True)
    return parser


def get_oracle(program_space, program_path):
    comp_result = run(program_space.compile_script, program_path)
    comp_succ = False if comp_result is None else True

    if comp_succ:
        run(program_space.execute_script, program_path)
    else:
        raise Exception('Compilation failed.')

    return os.path.join(program_path, 'trajectory')


if __name__ == '__main__':

    parser = get_parser()
    args = parser.parse_args()

    program_space = ProgramSpace(args.proj_name)
    orig_path = os.path.join(program_space.proj_path, 'orig')
    temp_proj_path = '/tmp/temp_proj_path'

    if os.path.isdir(temp_proj_path):
        shutil.rmtree(temp_proj_path)
    shutil.copytree(orig_path, temp_proj_path)

    oracle_path = get_oracle(program_space, temp_proj_path)

    if os.path.isdir(os.path.join(program_space.proj_path, 'oracle')):
        shutil.rmtree(os.path.join(program_space.proj_path, 'oracle'))
    shutil.copytree(oracle_path,
                    os.path.join(program_space.proj_path, 'oracle'))
