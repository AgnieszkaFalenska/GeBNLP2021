#!/usr/bin/env python

import sys, os
import json
import re
import string
import logging

import projpath
import lang.lang_processor as lp
from stats.stat_utils import getTupleKey
    
def countTitleTuples(filenames):
    result = { }
    for filename in filenames:
        for line in open(filename, "r"):
            cat, wTitle, mTitle, gTitle = line.strip().split('\t')
            pKey = getTupleKey(wTitle, mTitle, gTitle)
        
            cat = cat.split("=")[1][:-1]
            result.setdefault(pKey, {})
            result[pKey].setdefault(cat, 0)
            result[pKey][cat] += 1
        
    return result
    
if __name__ == "__main__":
    lformat = '[%(levelname)s] %(message)s'
    logging.basicConfig(stream=sys.stdout, level=logging.getLevelName("INFO"), format=lformat)
    
    genTitlesFilenames = sys.argv[1:]
    
    print(countTitleTuples(genTitlesFilenames))
    
