# DM

## Requirements

- python 3.6
- srcml (optional)

### Python Package

- numpy

## Installation

- Set MOAD_HOME to MOAD repository root directory

## Run (Tutorial)

1. Create project folder in `output/original`
   - It should contains source file, test script and configuration file explaining the contents
   - Check the example project folder in `output/original` directory.
2. Run `oracle.py` to generate oracle trajectory of criteria.
    > python oracle.py -p mbe
3. Run `main.py` to generate observations.
    > python main.py -p mbe -f line -d onehot -i 1000 -o line-onehot --save_generated --save_log
4. Run `model.py` to infer slice from the model trained by the observations.
    > python model.py -p mbe -d line-onehot -i once_success --save_generated --save_log
## Preparation: create `original` directory for the project under analysis

### Structure

```s
$ tree output/original/mbe/
output/original/mbe/
├── config
│   └── config.ini
├── orig
│   ├── mbe.c
│   └── mbe_original.c
└── scripts
    ├── compile.sh
    ├── criteria
    ├── execute.sh
    ├── terminate.sh
    └── testsuite
        ├── testcase1.sh
        ├── testcase2.sh
        ├── testcase3.sh
        └── testcase4.sh
4 directories, 11 files
```

Above shows an example directory structure of a program `mbe`.
The `original` directory needs three elements.
1) Configuration
2) Source code
3) Scripts

### Configuration

The configuration file should contains information as below.

```ini
$ cat output/original/mbe/config/config.ini
[COMMON]

[PROGRAMSPACE]
orig_dir = "the directory containing source codes (e.g. orig)"
files = "target source code file names in `orig_dir` (e.g. mbe.c)"

[SCRIPT]
script_dir = "the directory containing script files (e.g. scripts)"
compile_script = "compilation script filename (e.g. compile.sh)"
execute_script = "execution script filename (e.g. execute.sh)"
terminate_script = "the script filename which clean up the generated files (e.g. terminate.sh)"
```

### Source code

With respect to the source code in the original project to analyze, MOAD needs pair of the source code files for each source code file in the original project. 

- {filename}_original: the same file in the original project
- {filename}: the annotated version of the file in the original project

You could check the differece between two in the given example projects. Annotation is automatically done using `clang` for given exmaples projects.

### Scripts

MOAD needs three script files and a single criteria file to run the experiment.

#### 1) Compilation script

```s
$ cat output/original/mbe/scripts/compile.sh 
#!/bin/bash

cd $1

rm -rf mbe.exe &> /dev/null

gcc -o mbe.exe mbe.c &> compile.log

if [ -e 'mbe.exe' ]; then
    md5sum mbe.exe
else
    exit -1
fi
```

Above shows a compilation script of the program mbe. A compilation script requires two things:

1. it needs to compile the target project, and
2. the return value needs to be unique concerning the compilation result.

The second requriment is needed to cache the compilation result so that MOAD can skip redundant execution.

#### 2) Execution script

```s
$ cat output/original/mbe/scripts/execute.sh 
#!/bin/bash

orig_path="$MOAD_HOME/output/original/mbe"

numtc=$(ls -1q ${orig_path}/scripts/testsuite/ | wc -l)
numcrit=$(cat ${orig_path}/scripts/criteria | wc -l)
ret=""

cd $1

mkdir -p outputs

for i in $(seq 1 $numtc); do
    timeout --signal=KILL 0.1 $orig_path/scripts/testsuite/testcase${i}.sh >./outputs/output${i}
done

for i in $(seq 1 $numtc); do
    mkdir -p trajectory/testcase${i}
    crit_idx=0
    for crit in $(cat $orig_path/scripts/criteria); do
        crit_idx=$((crit_idx + 1))
        grep $crit ./outputs/output${i} >trajectory/testcase${i}/tj${crit_idx}
        cmp --silent $orig_path/oracle/testcase${i}/tj${crit_idx} trajectory/testcase${i}/tj${crit_idx}
        ret="${ret}$?"
    done
done

echo $ret
```

Above shows an execution script of the program mbe. An execution script do three things:

1. it runs the test suite on the compiled program, and
2. it compares the trajectory of each slicing critria to the oracle.

What an execution script returns is a string of binary value indicates representing whether the trajectory is the same with the oracle or not.

#### 3) Termination script

```s
$ cat output/original/mbe/scripts/terminate.sh
#!/bin/bash

cd $1

rm -rf compile.log mbe.exe outputs/ trajectory/
```

Above shows a termination script of the program mbe. A termination script erases executable and trajectories to observe on new program.


#### 4) Criteria file

```s
$ cat output/original/mbe/scripts/criteria
ORBS:12:5:j
ORBS:13:5:k
ORBS:14:14:j
...
ORBS:49:12:k
ORBS:53:12:k
ORBS:57:12:j
```

A criteria file is a list of criteria in the project under analysis.

## `oracle.py`

```s
$ python oracle.py -h
usage: oracle.py [-h] -p PROJ_NAME

optional arguments:
  -h, --help            show this help message and exit
  -p PROJ_NAME, --proj_name PROJ_NAME
                        Target project name
```

`oracle.py` runs the (annotated) original project and stores the oracle trajectory of the slicing criteria.

## `main.py`

```s
$ python main.py -h
usage: main.py [-h] -p PROJ_NAME [-f {line,srcml}]
               [-d {onehot,random,nhot,ff2l,2hot,random_1000,random_2000}]
               [--doe_random_threshold DOE_RANDOM_THRESHOLD] [--max_n MAX_N]
               [-i MAX_EXPR] [-o OUTPUT_NAME] [--save_generated] [--save_log]
               [--seed SEED] [--planned_idx PLANNED_IDX PLANNED_IDX]

optional arguments:
  -h, --help            show this help message and exit
  -p PROJ_NAME, --proj_name PROJ_NAME
                        Target project name
  -f {line,srcml}, --factor_level {line,srcml}
                        Factor level
  -d {onehot,random,nhot,ff2l,2hot,random_1000,random_2000}, --doe_strategy {onehot,random,nhot,ff2l,2hot,random_1000,random_2000}
                        Design of experiment strategy
  --doe_random_threshold DOE_RANDOM_THRESHOLD
                        DoE random strategy threshold
  --max_n MAX_N         Maximum combination for One2NHotDoE
  -i MAX_EXPR, --max_expr MAX_EXPR
                        Maximum number of the experiment
  -o OUTPUT_NAME, --output_name OUTPUT_NAME
                        Output(model) saving folder name
  --save_generated      Save all generated programs
  --save_log            Save log
  --seed SEED           Random seed
  --planned_idx PLANNED_IDX PLANNED_IDX
                        Range of pre-planned idx, from "start" to "end-1". If
                        start == end, the range covers whole
```

`main.py` observes the trajectory of various partially deleted program and compares it with the oracle. There are two level of deletable unit (factor): **line** and **srcml**. Srcml represents AST-level. To use it, it needs to install srcml. There are various kinds of deletion generation scheme: `onehot`, `nhot` (including `2hot`), `random`, etc.


## `model.py`

```s
$ python model.py -h
usage: model.py [-h] -p PROJ_NAME -d DATA_NAME [-f {line,srcml}] -i
                {once_success,logistic,simple_bayes} [--save_generated]
                [--save_log] [--sub_sample SUB_SAMPLE]
                [--output_path OUTPUT_PATH] [--seed SEED]

optional arguments:
  -h, --help            show this help message and exit
  -p PROJ_NAME, --proj_name PROJ_NAME
                        Target project path
  -d DATA_NAME, --data_name DATA_NAME
                        Data dir name
  -f {line,srcml}, --factor_level {line,srcml}
                        Factor level
  -i {once_success,logistic,simple_bayes}, --inference {once_success,logistic,simple_bayes}
                        Inference algorithm
  --save_generated      Save all generated programs
  --save_log            Save log
  --sub_sample SUB_SAMPLE
                        Use only portion of the samples. [0.0 - 1.0]
  --output_path OUTPUT_PATH
                        Explicitly state out the output path
  --seed SEED           Numpy random seed
```

`model.py` gets the observation generated by `main.py` and infers the slice of the criteria. The `factor-level` needs to be the same with the one used on the `main.py`. There are three inference algorithms: `once_success`, `logistic`, and `simple_bayes`.


## Classes

### FactorManager

gets the factor, generate the program

### ResponseManager

gets the program, generate the response

### DoEManager

gets the response, generate the factor

## Output

The experiment results are stored in output directory.

### original

A directory that stores original project and other files necessary to run the experiments such as inputs, scripts, oracles, etc.

### experiment

A directory contains the observations of the experiments.
This results are constructed by the script `main.py`.

### model

A directory contains the model generated by the inference algorithm.
This results are constructed by the script `model.py`.
