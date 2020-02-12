#!/usr/bin/env bash

if [ "$1" -gt "-1" ]
then 
    bport=$1
else
    bport=5006
fi

python3 azure_usage/main.py --origin 0.0.0.0 --bport $bport 
