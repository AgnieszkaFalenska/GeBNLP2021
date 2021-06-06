#!/bin/bash

DIR=$(readlink -f $(dirname ${BASH_SOURCE[0]}))

## Project

export PROJPATH=$DIR/..
export CMD=$DIR

export INT_DIR=$PROJPATH/intermediate-data
export DATA_DIR=$PROJPATH/data
