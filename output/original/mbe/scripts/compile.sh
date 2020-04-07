#!/bin/bash

cd $1

rm -rf mbe.exe &> /dev/null

gcc -o mbe.exe mbe.c &> compile.log

if [ -e 'mbe.exe' ]; then
    md5sum mbe.exe
else
    exit -1
fi
