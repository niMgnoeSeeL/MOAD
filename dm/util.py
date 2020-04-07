import subprocess


def run(script_path, work_dir):
    try:
        ret = subprocess.run(
            ['source {} {}'.format(script_path, work_dir)],
            shell=True,
            executable='/bin/bash',
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            timeout=500,
            check=True)
    except subprocess.SubprocessError as e:
        return None
    else:
        return ret.stdout


def run_output(script_path, work_dir):
    try:
        ret = subprocess.run(
            ['source {} {}'.format(script_path, work_dir)],
            shell=True,
            executable='/bin/bash',
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            timeout=500,
            check=True)
    except subprocess.SubprocessError as e:
        print('# Subprocess error occured.')
        print('#\t message: {}'.format(ret.stdout.decode('utf-8')))
        exit(1)
    else:
        return ret.stdout.decode('utf-8')


def shell_cmd(cmd):
    ret = subprocess.run(
        cmd,
        shell=True,
        executable='/bin/bash',
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT)
    if ret.returncode:
        print('# Subprocess error occured.')
        print('#\t command: {}'.format(cmd))
        print('#\t message: {}'.format(ret.stdout.decode('utf-8')))
        exit(1)
    else:
        return ret.stdout.decode('utf-8')
