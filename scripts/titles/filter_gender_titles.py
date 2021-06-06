#!/usr/bin/env python

import sys, os
import json
import re

import logging
import projpath

from lang.lang_utils import removePunctuation, splitByPunctuation
from lang.processor_builder import buildLangProcessor
from title_utils import getArticleKey, TitleGroup

def readLemmas(filename, result):
    for line in open(filename):
        parts = line.strip().split('\t')
        if len(parts) != 3:
            logging.warning("Wrong number of parts in line: %s" % line)
            continue
        
        _, title, lemmas = parts    
        result[title] = [ l.lower() for l in lemmas.split() ]
        
def getTitleWords(title):
    titleWords = splitByPunctuation(title)
    titleWords = [removePunctuation(t.lower()) for t in titleWords ]
    return [ w for w in titleWords if len(w) > 0 ]
        
def fillGeneralTitles(titleGroup, lang, allLemmas, allKeys, genderedIds):
    generalKeys = set([ ])
    for (wTitle, wId) in titleGroup.womenIds:
        wTitleWords = getTitleWords(wTitle)
        wLemmas = allLemmas[wTitle]
        keys = [ getArticleKey(p) for p in lang.getGeneralOptions(wTitleWords, wLemmas) ]
        generalKeys |= set([ gk for gk in keys if gk in allKeys])
           
    for (mTitle, mId) in titleGroup.menIds:
        mTitleWords = getTitleWords(mTitle)
        mLemmas = allLemmas[mTitle]
        keys = [ getArticleKey(p) for p in lang.getGeneralOptions(mTitleWords, mLemmas) ]
        generalKeys |= set([ gk for gk in keys if gk in allKeys])
    
    for gk in generalKeys:
        for gkTitle, gkId in allKeys[gk]:
            if gkId not in genderedIds:
                titleGroup.generalIds.add((gkTitle, gkId))
                
def findGenderedTitles(filename, allLemmas, allKeys, redirTitles, lang):
    def __findTitleGroup(keys):
        # find first instance
        titleGroup = None
        for kOpt in keys:
            if kOpt in genderKeys:
                titleGroup = genderKeys[kOpt]
                break
        
        # set all keys to the same instance
        if titleGroup is None:
            titleGroup = TitleGroup()
            titleGroups.append(titleGroup)
        
        return titleGroup
        
    genderIds = set([])
    genderKeys = { }
    titleGroups = [ ]
    allOmmited = 0
    for line in open(filename):
        articleId, title, lemmas = line.strip().split('\t')
        titleWords = getTitleWords(title)
        
        if len(getArticleKey(titleWords)) < 2:
            logging.debug("Ommiting regular title: %s" % title)
            allOmmited += 1
            continue
        
        lemmas = [ l.lower() for l in lemmas.split() ]
        allLemmas[title] = lemmas
        
        # lemmas key
        fullKey = getArticleKey(lemmas)
        allKeys.setdefault(fullKey, [ ])
        allKeys[fullKey].append((title, articleId))

        # title key
        titleKey = getArticleKey(titleWords)
        allKeys.setdefault(titleKey, [ ])
        allKeys[titleKey].append((title, articleId))
        
        isWoman = lang.isLangWomanTitle(title, titleWords, lemmas)
        isMan = lang.isLangManTitle(title, titleWords, lemmas)
        
        # we don't want both
        if isWoman and isMan:
            continue
        
        # we want at least one    
        if not isWoman and not isMan:
            continue
        
        # all ids with info about gender
        genderIds.add(articleId)
        
        # key options
        filteredLemmas = lang.filterGenderInformation(lemmas)
        filteredTitle = lang.filterGenderInformation(titleWords)
        articleKeys = [ getArticleKey(kOpt) for kOpt in [ filteredLemmas, filteredTitle ] ]
        
        # find first instance
        titleGroup = __findTitleGroup(articleKeys)
        for kOpt in articleKeys:
            genderKeys[kOpt] = titleGroup
            genderKeys[kOpt].allKeys.add(kOpt)
            
            if isWoman:
                genderKeys[kOpt].womenIds.add((title, articleId))
            
            if isMan:
                genderKeys[kOpt].menIds.add((title, articleId))
        
    logging.info("Ommited regular titles: %i" % allOmmited)
    for titleGroup in titleGroups:
        fillGeneralTitles(titleGroup, lang, allLemmas, allKeys, genderIds)
       
    return titleGroups
    
def readRedirKeys(redirs, allLemmas, allKeys, allRedirs):
    allOmmited = 0
    for line in open(redirs):
        articleId, articleType, title, redirId, redirType = line.strip().split('\t')
        titleWords = getTitleWords(title)
        
        if redirType != "[ARTICLE]":
            continue

        if len(getArticleKey(titleWords)) < 2:
            logging.debug("Ommiting redirect title: %s" % title)
            allOmmited += 1
            continue
    
        # title key
        titleKey = getArticleKey(titleWords)
        allKeys.setdefault(titleKey, [ ])
        allKeys[titleKey].append((title, redirId))
        
        # lemma key
        lKey = getArticleKey(allLemmas[title])
        allKeys.setdefault(lKey, [ ])
        allKeys[lKey].append((title, redirId))
        
        allRedirs.setdefault(redirId, [ ])
        allRedirs[redirId].append(title)
    
    logging.info("Ommited redirect titles: %i" % allOmmited)
    
if __name__ == "__main__":
    lformat = '[%(levelname)s] %(message)s'
    logging.basicConfig(stream=sys.stdout, level=logging.getLevelName("INFO"), format=lformat)

    titlesWithLemmas = sys.argv[1]
    lang = buildLangProcessor(sys.argv[2])
    
    out = open(sys.argv[3], "w")
    
    redirLemmas = { }
    redirKeys = { }
    redirTitles = { }
    if len(sys.argv) > 4:
        redirs = sys.argv[4]
        redirsWithLemmas = sys.argv[5]
    
        readLemmas(redirsWithLemmas, redirLemmas)
        logging.info("Redir lemmas: %i" % len(redirLemmas))
    
        # reading redir info
        readRedirKeys(redirs, redirLemmas, redirKeys, redirTitles)
        logging.info("Redir keys: %i" % len(redirKeys))
      
    genderedTitles = findGenderedTitles(titlesWithLemmas, redirLemmas, redirKeys, redirTitles, lang)
    for titles in genderedTitles:
        toPrint = [ str(t) for t in titles.buildFullInfo() ]
        out.write('\t'.join(toPrint) + "\n")
