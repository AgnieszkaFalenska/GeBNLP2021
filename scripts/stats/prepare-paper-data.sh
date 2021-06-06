#!/bin/bash

set -ue

D=$(readlink -f $(dirname ${BASH_SOURCE[0]}))
source $D/../get_global_vars.sh

LANG=$1

if [ $# -gt 1 ]; then
    FREEZE=$2
else
    FREEZE=`date +'%d_%m_%Y'`
fi

OUT_DIR=$PROJPATH/for_paper/$FREEZE

if [ ! -e $OUT_DIR ]; then
    mkdir -p $OUT_DIR
fi

TITLES_IN=$INT_DIR/$LANG/titles/wiki_gender_titles.redirs.cats.txt
TITLES=$OUT_DIR/$LANG.titles.txt
cp $TITLES_IN $TITLES 

$CMD/plots/group_titles.py $TITLES $OUT_DIR no

