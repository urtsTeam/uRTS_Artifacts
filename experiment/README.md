# Experiment

## Setup Environment
```
$ ./setup_ubuntu.sh
```

## Install uRTS

Use the following command to install uRTS:
```
$ ./install_urts.sh
```

## Run Experiment
Use `run.sh` script to run `ReTestAll` or `uRTS` experiments in our evaluation.
```
$ ./run.sh <mode> <project>
```
`<mode>` can be `urts` or `retestall`;\
`<project>` can be `hcommon`, `hdfs`, `hbase`, `alluxio` or `zookeeper`.

## Check Experiment Results
The script will automatically extract test execution time and number data into `csv` files.\
For example, to check uRTS HCommon results, execute:
```
$ cat uRTS/hcommon/result.csv
```
