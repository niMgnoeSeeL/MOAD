#!/bin/bash

cd $1

rm -rf wc.exe &> /dev/null

gcc -o wc.exe wc.c &> compile.log

if [ -e 'wc.exe' ]; then
    md5sum wc.exe
else
    exit -1
fi
