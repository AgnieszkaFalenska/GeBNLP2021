#!/usr/bin/env python

import sys, os
import json
import gzip, bz2
import re, codecs
import projpath

from lang.processor_builder import buildLangProcessor
import wiki_utils
import string
 
def removePunctuation(word):
    return "".join([ c for c in word if (c not in string.punctuation) ])

def splitByPunctuation(word):
    result = ""
    for c in word:
        if c in string.punctuation + "“‚‘":
            result += " " + c + " "
        else:
            result += c
            
    return [ w for w in result.split() if len(w) > 0 ]

def isInterestingWord(lang, word):
    for pref in lang.womenWords + lang.menWords:
        if word.startswith(pref):
            return True
        
    for suffix in lang.womenSuffixes:
        if word.endswith(suffix):
            return True
        
    return False

def removePrefixInfo(lang, word):
    for _, gi in lang.genderInfo:
            if word.startswith(gi):
                return word[len(gi):]
    
    return None

def removeSuffixInfo(lang, word):
    for suffix in lang.womenSuffixes:
        if word.endswith(suffix):
                shorter = word[:-len(suffix)]
                return shorter
    return None

def readAllWords(filename):
    result = { }
    for line in open(filename, "r"):
        if len(line.strip().split('\t')) < 2:
            continue
            
        word, freq = line.strip().split('\t')
        result[word] = int(freq)
    return result
    
def getAllWords(allFiles):
    for filename in allFiles:
        print(filename)
        for line in open(filename, "r"):
            page = json.loads(line)
            
            text = page["text"] + " " + page["title"]
            for w in text.lower().split():
                
                words = [ removePunctuation(w) ]
                words += splitByPunctuation(w)
                
                for ww in words:
                    allWords.setdefault(ww, 0)
                    allWords[ww] += 1
                    
if __name__ == "__main__":
    # extracted wiki
    inDir = sys.argv[1]
    lang = buildLangProcessor(sys.argv[2])
    out = open(sys.argv[3], "w")
    outAll = sys.argv[4]
    
    if os.path.exists(outAll):
        allWords = readAllWords(outAll)
    else:
        allFiles = wiki_utils.getFiles(inDir)
        allWords = getAllWords(allFiles)
        
    allGenderWords = set([])
    for ww, freq in allWords.items():
        if isInterestingWord(lang, ww):
            allGenderWords.add(ww)
                    
    print("All words", len(allWords))
    for gw in allGenderWords:
        pShorter = removePrefixInfo(lang, gw)
        sShorter = removeSuffixInfo(lang, gw)
        
        if pShorter is not None and pShorter in allWords:
            if len(pShorter) < 5:
                continue
                
            #print(gw, pShorter, allWords[pShorter])
            out.write(gw + "\n")
                    
        elif sShorter is not None:
            if len(sShorter) < 5 or gw.endswith("spinnen"):
                continue
                
            if sShorter in allWords:
                pass
            elif (sShorter + "e") in allWords:
                sShorter += "e"
            elif (sShorter + "n") in allWords:
                sShorter += "n"
            elif (sShorter + "en") in allWords:
                sShorter += "en"
            else:
                continue
                
            if allWords[sShorter] < 20:
                continue
                
            out.write(gw + "\n")
