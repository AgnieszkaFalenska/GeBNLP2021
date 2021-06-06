#!/usr/bin/env python

import os, sys
import logging

from lang.lang_utils import removePunctuation, splitByPunctuation

UNKNOWN_CAT = "unknown"
NOT_INTERESTING_CAT = "not_interesting"
LIST_CAT = "list"
NAME_CAT = "name"
WEAK_LIST_CAT = "weak_list"
SPORT_CAT = "sport"
ART_CAT = "art"
GEO_CAT = "geo"
BUILDING_CAT = "building"
SOCIAL_CAT = "social"
BIO_CAT = "bio"
            
MATCH_INFO = {
    NOT_INTERESTING_CAT : False,
    UNKNOWN_CAT : True,
    LIST_CAT : True,
    NAME_CAT : False,
    WEAK_LIST_CAT : True,
    SPORT_CAT : True,
    ART_CAT : False,
    GEO_CAT : False,
    BUILDING_CAT : False,
    SOCIAL_CAT : True,
    BIO_CAT : False
    }

PROPER_NAMES = [ NAME_CAT, ART_CAT, GEO_CAT, BUILDING_CAT, BIO_CAT ]

class CatProcessor(object):
    def __init__(self, lang):
        self.catFilters = self.__readCatFilters(lang)
        
        self.wikiContentDisamb = [ "{{disambiguation}}", "{{ujednoznacznienie}}", "{{begriffsklärung}}", "{{anlam ayrımı}}" ]
        self.wikiTitleDisamb = [ "(disambiguation)", "(ujednoznacznienie)", "(begriffsklärung)", "(anlam ayrımı)" ] 
        

    ### category functions

    def getMainCategoryName(self, catName):
        assert type(catName) == type("")
        
        words = self.__getCategoryWords(catName)
        return self.__getCategoryName(words)
        
    def getArticleCategory(self, artTitle, artCats):
        assert type(artTitle) == type("")
        assert type(artCats) == type([])
        
        words = self.__getTitleWords(artTitle)
        
        strongTitleFilters = [ NOT_INTERESTING_CAT, SPORT_CAT, LIST_CAT, ART_CAT, WEAK_LIST_CAT ]
            
        for cat in strongTitleFilters:
            if self.__matchTitle(cat, words):
                return cat
               
        strongCats = [ BIO_CAT, LIST_CAT, SPORT_CAT, ART_CAT, SOCIAL_CAT, NAME_CAT, GEO_CAT, BUILDING_CAT ]
        
        mostFreq = self.__selectMostFreqCats(artCats)
        
        # first most common
        for cat in strongCats:
            if cat in mostFreq:
                return cat
                
        # second -- any cat
        for cat in strongCats:
            if cat in artCats:
                return cat
                
        weakTitleFilters = [SOCIAL_CAT, GEO_CAT, BUILDING_CAT, BIO_CAT, NAME_CAT ]
        for cat in weakTitleFilters:
            if self.__matchTitle(cat, words):
                return cat
                
        weakCats = [  WEAK_LIST_CAT ]
        
        for cat in weakCats:
            if cat in artCats:
                return cat
                
        return UNKNOWN_CAT
        
    def isInterestingCategory(self, categoryName):
        assert type(categoryName) == type("")
        
        words = categoryName.split("_")
        if len(words) < 1 or ":" in words[0]:
            return False     
        
        words = self.__getCategoryWords(categoryName)
        return not self.__matchCategory(NOT_INTERESTING_CAT, words)
    
    ## searching for categories
    
    def __getCategoryName(self, words):
    
        order = [ NOT_INTERESTING_CAT, LIST_CAT, NAME_CAT, WEAK_LIST_CAT, SPORT_CAT,
                  ART_CAT, GEO_CAT, BUILDING_CAT, SOCIAL_CAT, BIO_CAT ]
        
        for cat in order:
            if self.__matchCategory(cat, words):
                return cat
            
        return None
    
    ## matching categories
    
    def __readCatFilters(self, lang):
        thisFile = os.path.realpath(__file__)
        thisPath = os.path.dirname(thisFile)
        
        result = { }
        for line in open(thisPath + "/" + lang + ".cat_rules.txt", "r"):
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            
            info, words = line.split("=")
            catName, fType, matchType = info.split(".")
            
            if catName not in MATCH_INFO:
                logging.error("Unknown category %s" % catName)
                sys.exit()
                
            result.setdefault(catName, { })
            
            if fType not in [ "title", "cat" ]:
                logging.error("Unknown filter type %s" % fType)
                sys.exit()
            
            result[catName].setdefault(fType, { })
               
            matchType = matchType.strip()
                       
            if matchType not in [ "words", "prefixes", "suffixes", "full", "full_prefixes", "non_words", "full_non_prefixes", "full_suffixes", "full_non_suffixes" ]:
                logging.error("Unknown match type %s" % matchType)
                sys.exit()
                      
            result[catName][fType][matchType] = [ w.strip() for w in words.split(",") ]
            
        return result
       
    def __matchCategory(self, category, words):
        if category not in self.catFilters or "cat" not in self.catFilters[category]:
            return False
            
        return self.__matchFilters(self.catFilters[category]["cat"], words)
        
    def __matchTitle(self, category, words):
        if category not in self.catFilters or "title" not in self.catFilters[category]:
            return False
            
        return self.__matchFilters(self.catFilters[category]["title"], words)
    
    def __matchFilters(self, filters, words):
        fullName = "_".join(words)
        
        ## full
        if "full" in filters and fullName in filters["full"]:
            return True
        
        ## full_prefixes
        if "full_prefixes" in filters:
            if any([fullName.startswith(prefix) for prefix in filters["full_prefixes"]]):
                return True
        
        if "full_suffixes" in filters:
            if any([fullName.endswith(suffix) for suffix in filters["full_suffixes"]]):
                return True
            
        ## non words
        if "full_non_prefixes" in filters:
            if any(fullName.startswith(prefix) for prefix in filters["full_non_prefixes"]):
                return False
            
        ## non words
        if "full_non_suffixes" in filters:
            if any(fullName.endswith(suffix) for suffix in filters["full_non_suffixes"]):
                return False
            
        ## non words
        if "non_words" in filters:
            if any([word in filters["non_words"] for word in words]):
                return False
            
        ## suffixes
        if "suffixes" in filters:
            for word in words:
                if any([word.endswith(suffix) for suffix in filters["suffixes"]]):
                    return True
        
        ## prefixes
        if "prefixes" in filters:
            for word in words:
                if any([word.startswith(prefix) for prefix in filters["prefixes"]]):
                    return True

        ## words                    
        if "words" in filters:
            return any([word in filters["words"] for word in words])

        return False
        
    ## private helpers
   
    def __getCategoryWords(self, catName):
        words = splitByPunctuation(catName)
        words = [ removePunctuation(w.lower()) for w in words ]
        return [ w for w in words if len(w) > 0 ]
    
    def __getTitleWords(self, title):
        words = splitByPunctuation(title)
        words = [ removePunctuation(w.lower()) for w in words ]
        return [ w for w in words if len(w) > 0 ]
        
    def __selectMostFreqCats(self, artCats):
        result = { }
        for catName in artCats:
            if catName in [ UNKNOWN_CAT, NOT_INTERESTING_CAT ]:
                continue
                    
            result.setdefault(catName, 0)
            result[catName] += 1
        
        if len(result) == 0:
            return [ ]
            
        result = [ (f, k) for (k, f) in result.items()]
        result.sort(reverse=True)
            
        bestFreq = result[0][0]
        return [ k for (f, k) in result if f == bestFreq ]
