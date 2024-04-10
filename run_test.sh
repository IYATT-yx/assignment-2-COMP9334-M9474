#!/usr/bin/env sh

if [ "$1" = "r" ];
then
    rm -rf ./output/*
    echo "./output/* deleted"
else
    python3 main.py $1
fi