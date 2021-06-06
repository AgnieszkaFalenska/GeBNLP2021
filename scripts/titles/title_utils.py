#!/usr/bin/env python

import sys, os
import json
import re
import string
import logging

import projpath
from lang.lang_utils import removePunctuation

def readInfo(filename):
    result = { }
    for line in open(filename, "r"):
        articleId, cats = line.strip().split('\t')
        result[articleId] = cats
    return result


def getArticleCats(articleId, pageCats):
    if articleId not in pageCats:
        logging.info("Unknown articleID: %s" % articleId)
        return [ ]
    
    return pageCats[articleId].split(",")
    
def parsePages(pages):
    result = [ ]
    if pages == "None":
        return result
            
    for page in pages.split("#<>#"):
        match = re.match("\[(\d+)\]\s(.*)", page)
        pId, pTitle = match.group(1), match.group(2)
        result.append((pId, pTitle))
        
    return result
        
def getArticleKey(lemmas):
    assert type(lemmas) == type([])
    return "".join(sorted([ removePunctuation(l) for l in lemmas]))

class TitleGroup(object):
    def __init__(self):
        self.allKeys = set([])
        self.menIds = set([])
        self.womenIds = set([])
        self.generalIds = set([])
    
    def __buildInfo(self, ids, withIds=True):
        if len(ids) == 0:
            return "None"
        
        if withIds:
            result = "#<>#".join(["[" + tId + "]" + " " + title for (title, tId) in ids ])
        else:
            result = "#<>#".join([title for (title, _) in ids ])
        #if len(ids) > 1:
        #    print("More than one title", result)
        
        return result

    def buildFullInfo(self):
        return (self.__buildInfo(self.womenIds),
                self.__buildInfo(self.menIds),
                self.__buildInfo(self.generalIds))
        
    def buildTitleInfo(self):
        return (self.__buildInfo(self.womenIds, withIds=False),
                self.__buildInfo(self.menIds, withIds=False),
                self.__buildInfo(self.generalIds, withIds=False))
                
    def buildTitleStr(self):
        return '\t'.join(self.buildTitleInfo())
    
    def __str__(self):
        return '\t'.join(self.buildFullInfo())
