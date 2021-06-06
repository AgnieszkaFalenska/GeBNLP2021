#!/usr/bin/env python

import sys, os
import json
import re
import string
import logging

import projpath
from lang import cat_processor as lp

def groupTitleTuples(filename, filters):
    result = { }
    for line in open(filename, "r"):
        cat, wTitle, mTitle, gTitle = line.strip().split('\t')
        
        cat = cat.split("=")[1][:-1]
        if cat in filters:
            continue
        
        pKeys = [ ]
        if wTitle != "None":
            pKeys.append("w")
            
        if mTitle != "None":
            pKeys.append("m")
            
        if gTitle != "None":
            pKeys.append("g")
            
        pKey = "_".join(pKeys)
        result.setdefault(pKey, [ ])
        result[pKey].append(line)
        
    return result

if __name__ == "__main__":
    lformat = '[%(levelname)s] %(message)s'
    logging.basicConfig(stream=sys.stdout, level=logging.getLevelName("INFO"), format=lformat)
    
    genTitlesFilename = sys.argv[1]
    outDir = sys.argv[2]

    if sys.argv[3] in [ "y", "yes", "filter" ]:
        suff = ".no-names."
        filters = lp.PROPER_NAMES
    else:
        suff = ".names."
        filters = [ ]
    
    groups = groupTitleTuples(genTitlesFilename, filters=filters)
    for (groupName, titles) in groups.items():
        outFilename = genTitlesFilename.split("/")[-1].replace(".txt", suff + groupName + ".txt")
        out = open(outDir + "/" + outFilename, "w")
        for line in sorted(titles):
            out.write(line)
        out.close()
