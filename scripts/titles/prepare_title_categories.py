#!/usr/bin/env python

import sys, os
import json
import re
import string
import logging

import projpath
import title_utils
from lang.processor_builder import buildLangProcessor
from lang.cat_processor import UNKNOWN_CAT, NOT_INTERESTING_CAT
    
def readGenderedTitles(filename):
    result = { }
    for line in open(filename, "r"):
        wPages, mPages, gPages = line.strip().split('\t')
        wPages = title_utils.parsePages(wPages)
        mPages = title_utils.parsePages(mPages)
        gPages = title_utils.parsePages(gPages)
       
        for (pId, pTitle) in wPages + mPages + gPages:
            result[pId] = pTitle
            
    return result
    
def niceCategoryName(startCat, cats, subCats, lang, acc):
    def __findMainCategory(ids, filterCat=None):
        assert type(ids) == type(set()) or type(ids) == type(list())
        
        result = { }
        for cId in ids:
            if cId in acc:
                resultName = acc[cId]
            else:
                catName = cats[cId]
                resultName = lang.catProcessor.getMainCategoryName(catName)
            
            if filterCat is not None and resultName == filterCat:
                continue
                
            if resultName is not None:
                result.setdefault(resultName, 0)
                result[resultName] += 1
        
        if len(result) == 0:
            return None
        
        result = [ (f, k) for (k, f) in result.items()]
        result.sort(reverse=True)
        return result[0][1]
    
    mainCat = __findMainCategory([startCat])
    if mainCat is not None:
        acc[startCat] = mainCat
        return mainCat
    
    catIds = set([ startCat ])
    steps = lang.catSteps
    while steps > 0:
        newCats = set([])
        for catId in catIds:
            if catId in subCats:
                newCats |= set(subCats[catId].split(","))
        
        mainCat = __findMainCategory(newCats, NOT_INTERESTING_CAT)
        if mainCat is not None:
            acc[startCat] = mainCat
            return mainCat
    
        catIds |= newCats
        
        steps -= 1
        
    logging.debug("No main category name found: %s" % ",".join([cats[cId] for cId in catIds ]))
    acc[startCat] = UNKNOWN_CAT
    return UNKNOWN_CAT


def buildMainCategoryNames(genTitles, cats, subCats, lang):
    result = { }
    for (pId, pTitle) in genTitles.items():
        pCats = title_utils.getArticleCats(pId, pageCats)
        for pCat in pCats:
            if pCat in result:
                continue
                
            catMainName = niceCategoryName(pCat, cats, subCats, lang, result)
            result[pCat] = catMainName
            
    return result

def buildMainArticleCats(genTitles, cats, pageCats, catNames, lang):
    articleCats = { }
    for (pId, pTitle) in genTitles.items():
        pCats = title_utils.getArticleCats(pId, pageCats)
        pCatsNames = [ catNames[cId] for cId in pCats ]
        mainName = lang.catProcessor.getArticleCategory(pTitle, pCatsNames)
        
        if mainName == UNKNOWN_CAT:
            logging.debug("No category for article: %s %s" % (pTitle, ",".join([cats[cId] for cId in pCats])))
            
        articleCats[(pId, pTitle)] = mainName
            
    return articleCats

if __name__ == "__main__":
    lformat = '[%(levelname)s] %(message)s'
    logging.basicConfig(stream=sys.stdout, level=logging.getLevelName("INFO"), format=lformat)
    
    genTitlesFilename = sys.argv[1]
    categoriesFilename = sys.argv[2]
    pageCategoriesFilename = sys.argv[3]
    subCategoriesFilename = sys.argv[4]
    
    lang = buildLangProcessor(sys.argv[5])
    outCategories = open(sys.argv[6], "w")
    outArticles = open(sys.argv[7], "w")
    
    genTitles = readGenderedTitles(genTitlesFilename)
    cats = title_utils.readInfo(categoriesFilename)    
    pageCats = title_utils.readInfo(pageCategoriesFilename)
    subCats = title_utils.readInfo(subCategoriesFilename)
    
    catNames = buildMainCategoryNames(genTitles, cats, subCats, lang)
    
    allCatUnknown = 0
    for (catId, mainName) in catNames.items():
        catName = cats[catId]
        if mainName == UNKNOWN_CAT:
            allCatUnknown += 1
        outCategories.write(catId + '\t' + mainName + '\n')
    outCategories.close()
    
    catArticles = buildMainArticleCats(genTitles, cats, pageCats, catNames, lang)
        
    allArticleUnknown = 0
    for ((pId, pTitle), mainName) in catArticles.items():
        if mainName == UNKNOWN_CAT:
            allArticleUnknown += 1
            
        outArticles.write(pId + '\t' + mainName + '\n')
    outArticles.close()

    logging.info("Unknown categories: %i" % allCatUnknown)
    logging.info("Unknown articles: %i" % allArticleUnknown)        

