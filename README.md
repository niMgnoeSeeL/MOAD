# DM

## Requirements

- python 3.6

### Python Package

- numpy

## Installation

- Set DM_HOME to DM home directory

## Run

1. Create project folder in `output/original`
 - It should contains source file, test script and configuration file explaining the contents
2. Run `oracle.py` to generate oracle trajectory of criteria.
2. Insert criteria on the source file using `lib/insert_critria`.
3. Run `main.py` to generate observations.
4. Infer model.
    1) Run `model.py` to infer slice from the model trained by the observations.


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

### unit

A directory contains deletion units for cstmt level factor.
This results are constructed by the script `cstmt_unit.py`.

### experiment

A directory contains the observations of the experiments.
This results are constructed by the script `main.py`.

### model

A directory contains the model generated by the inference algorithm.
This results are constructed by the script `model.py`.
