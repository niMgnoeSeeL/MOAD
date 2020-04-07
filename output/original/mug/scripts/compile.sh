#!/bin/bash

cd $1

rm -rf mug.exe &> /dev/null

gcc -o mug.exe mug.c &> compile.log

if [ -e 'mug.exe' ]; then
    md5sum mug.exe
else
    exit -1
fi
