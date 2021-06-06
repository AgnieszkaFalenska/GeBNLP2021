#!/usr/bin/env python

import sys, os
import json
import re
import string
import logging

import projpath
import title_utils
from lang.processor_builder import buildLangProcessor
from lang import cat_processor as lp

def selectMostFreqCat(titleGroup, articleCats):
    result = { }
    for (articleTitle, articleId) in titleGroup.womenIds | titleGroup.menIds | titleGroup.generalIds:
        catName = articleCats[articleId]
            
        if catName in [ lp.UNKNOWN_CAT, lp.NOT_INTERESTING_CAT ]:
            continue
                    
        result.setdefault(catName, 0)
        result[catName] += 1
        
    if len(result) == 0:
        return lp.UNKNOWN_CAT
            
    result = [ (f, k) for (k, f) in result.items()]
    result.sort(reverse=True)
    return result[0][1]
        
def canBeMatched(pId, articleCats):
    pMainCat = articleCats[pId]
    return lp.MATCH_INFO[pMainCat]

def canBeMatchedGroup(titleGroup, articleCats):
    pMainCat = selectMostFreqCat(titleGroup, articleCats)
    return lp.MATCH_INFO[pMainCat]
    

def canBeMatchedWith(pTitle, pId, titlesInfo, titleGroup, articleCats):
    pMainCat = articleCats[pId]
    pGroupCat = selectMostFreqCat(titleGroup, articleCats)
    
    if pGroupCat == lp.SOCIAL_CAT and pMainCat in [ lp.GEO_CAT, lp.ART_CAT, lp.NAME_CAT ]:
        logging.debug("Exception for: %s [%s] %s [%s]" % (titlesInfo, pGroupCat, pTitle, pMainCat))
        return True
    
    if pGroupCat == lp.LIST_CAT and pMainCat in [ lp.GEO_CAT, lp.ART_CAT, lp.NAME_CAT ]:
        logging.debug("Exception for: %s [%s] %s [%s]" % (titlesInfo, pGroupCat, pTitle, pMainCat))
        return True
    
    return lp.MATCH_INFO[pMainCat]
    
def findCommonCategoriesForArticles(leftId, rightId, cats, pageCats, subCats, lang, steps):
    lCatIds = title_utils.getArticleCats(leftId, pageCats)
    rCatIds = title_utils.getArticleCats(rightId, pageCats)
    return findCommonCategoriesForCats(lCatIds, rCatIds, cats, subCats, lang, steps=steps)
    
def findCommonCategoriesForCats(lCatIds, rCatIds, cats, subCats, lang, steps):
    def __filterCats(catIds):
        return set([ cId for cId in catIds if lang.catProcessor.isInterestingCategory(cats[cId])])
        
    lCatIds = __filterCats(lCatIds)
    rCatIds = __filterCats(rCatIds)
    commonIds = lCatIds & rCatIds
    
    additionalGenderedSteps = lang.genderSteps
    while steps >= 0:
        if len(commonIds) > 0:
            return commonIds
        
        lNewCats = set([])
        for lCat in lCatIds:
            if lCat in subCats:
                lNewCats |= set(subCats[lCat].split(","))
        lCatIds |= __filterCats(lNewCats)

        rNewCats = set([])
        for rCat in rCatIds:
            if rCat in subCats:
                rNewCats |= set(subCats[rCat].split(","))
        rCatIds |= __filterCats(rNewCats)
        
        commonIds = lCatIds & rCatIds
        
        isGenderedCat = any([ lang.isGenderedCategory(cats[cId]) for cId in lNewCats | rNewCats])
        if isGenderedCat:
            additionalGenderedSteps -= 1
            if additionalGenderedSteps <= 0:
                break
        else:
            steps -= 1
        
    return commonIds
    
def filterByCategories(filename, cats, pageCats, subCats, articleCats, out):
    def __addSinglePage(pId, pTitle, titleGroups, isWomen):
        if pId in titleGroups:
            return
        
        titleGroups[pId] = title_utils.TitleGroup()
        titleGroups[pId].allKeys = title_utils.getArticleCats(pId, pageCats)
        if isWomen:
            titleGroups[pId].womenIds.add((pTitle, pId))
        else:
            titleGroups[pId].menIds.add((pTitle, pId))
               
                            
    for line in open(filename):
        wPages, mPages, gPages = line.strip().split('\t')
        wPages = title_utils.parsePages(wPages)
        mPages = title_utils.parsePages(mPages)
        gPages = title_utils.parsePages(gPages)
        
        titleGroups = { }
        
        # both types
        if len(wPages) > 0 and len(mPages) > 0:
            for (wId, wTitle) in wPages:
                for (mId, mTitle) in mPages:
                    if not canBeMatched(wId, articleCats) or not canBeMatched(mId, articleCats):
                        commonCats = None
                    else:
                        tSteps = lang.matchSteps
                        if len(wTitle.split()) > 5 and len(mTitle.split()) > 5:
                            tSteps += 5

                        commonCats = findCommonCategoriesForArticles(wId, mId, cats, pageCats, subCats, lang,  steps=tSteps)
                        
                    if commonCats is None or len(commonCats) == 0:
                        __addSinglePage(wId, wTitle, titleGroups, isWomen=True)
                        __addSinglePage(mId, mTitle, titleGroups, isWomen=False)
                        
                        if commonCats is None:
                            logging.info("Gendered [NON-MATCH]: %s [%s] %s [%s]" % (wTitle, articleCats[wId], mTitle, articleCats[mId]))
                        else:
                            logging.info("Gendered [NO-CAT]: %s [%s] %s [%s]" % (wTitle, articleCats[wId], mTitle, articleCats[mId]))
                    else:
                        titleGroups[(wId, mId)] = title_utils.TitleGroup()
                        titleGroups[(wId, mId)].allKeys = commonCats
                        titleGroups[(wId, mId)].womenIds.add((wTitle, wId))
                        titleGroups[(wId, mId)].menIds.add((mTitle, mId))
        # only women
        elif len(wPages) > 0:
            for (wId, wTitle) in wPages:
                __addSinglePage(wId, wTitle, titleGroups, isWomen=True)
        # only men
        elif len(mPages) > 0:
            for (mId, mTitle) in mPages:
                __addSinglePage(mId, mTitle, titleGroups, isWomen=False)
        # only general -- skip
        else:
            continue
                
        # add general
        for titleGroup in titleGroups.values():
            for (gId, gTitle) in gPages:
                titles = [ title for (title, _) in titleGroup.womenIds | titleGroup.menIds | titleGroup.generalIds ]
                titlesInfo = ",".join(titles)
                catInfo = selectMostFreqCat(titleGroup, articleCats)
               
                if not canBeMatchedGroup(titleGroup, articleCats) or not canBeMatchedWith(gTitle, gId, titlesInfo, titleGroup, articleCats):
                    logging.info("General [NON-MATCH]: %s [%s] %s [%s]" % (titlesInfo, catInfo, gTitle, articleCats[gId]))
                    continue
                
                tSteps = lang.matchSteps
                if all([len(title.split()) > 5 for title in titles]) and len(gTitle.split()) > 5:
                    tSteps += 5
                            
                gCats = title_utils.getArticleCats(gId, pageCats)
                commonCats = findCommonCategoriesForCats(gCats, titleGroup.allKeys, cats, subCats, lang, steps=tSteps)
                if len(commonCats) == 0:
                    logging.info("General [NO-CAT]: %s [%s] %s [%s]" % (titlesInfo, catInfo, gTitle, articleCats[gId]))
                else:
                    titleGroup.allKeys = commonCats
                    titleGroup.generalIds.add((gTitle, gId))

        
            mainCat = selectMostFreqCat(titleGroup, articleCats)
            out.write("[CAT=" + mainCat + "]\t" + titleGroup.buildTitleStr() + '\n')
        
if __name__ == "__main__":
    lformat = '[%(levelname)s] %(message)s'
    logging.basicConfig(stream=sys.stdout, level=logging.getLevelName("INFO"), format=lformat)
    
    categoriesFilename = sys.argv[1]
    pageCategoriesFilename = sys.argv[2]
    subCategoriesFilename = sys.argv[3]
    genTitlesFilename = sys.argv[4]
    articleCategoriesFilename = sys.argv[5]
        
    lang = buildLangProcessor(sys.argv[6])
    out = open(sys.argv[7], "w")
    
    cats = title_utils.readInfo(categoriesFilename)    
    pageCats = title_utils.readInfo(pageCategoriesFilename)
    subCats = title_utils.readInfo(subCategoriesFilename)
    articleCats = title_utils.readInfo(articleCategoriesFilename)
   
    filterByCategories(genTitlesFilename, cats, pageCats, subCats, articleCats, out)
    
        

