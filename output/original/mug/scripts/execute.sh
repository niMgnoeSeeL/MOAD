#!/bin/bash

orig_path="$DM_HOME/output/original/mug"

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
