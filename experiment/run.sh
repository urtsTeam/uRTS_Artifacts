#!/bin/bash

function usage() {
    echo 'Usage: ./run.sh [mode] [project]'
    echo '[mode]: (1) urts (2) retestall'
    echo '[project]: (1) hcommon (2) hbase (3) hdfs (4) alluxio (5) zookeeper'
    exit 1
}

function runExperiment() {
    if [ $project = "hcommon" ] || [ $project = "hbase" ] || [ $project = "hdfs" ] || [ $project = "alluxio" ] || [ $project = "zookeeper" ]
    then
        cd $mode/$project/
        echo '============== Start Running '$mode' '$project' =============='
        python3 run.py
        cd ../..
        echo '============== Finish Running '$mode' '$project' =============='
        echo '============== Extracting '$mode' '$project' data =============='
        python3 parse_result.py $mode $project
        echo 'Done!'
    else
        usage
    fi
}

mode=$1
project=$2

function main() {
    if [ -z $mode ] || [ -z $project ]; then
        usage
    elif [ $mode = "urts" ] || [ $mode = "retestall" ]; then
        runExperiment
    else
        usage
    fi
}

main