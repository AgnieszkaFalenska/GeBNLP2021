#!/usr/bin/env python

import projpath
from lang.lang_processor import LangProcessor

class EnglishLangProcessor(LangProcessor):
    def __init__(self):
        super().__init__("en")
        
        self.catSteps = 1
        
        # gender words
        
        ### articles with this words will be filtered
        self.womenWords = [ "women", "ladies", "women's", "womens", "female", "feminine" ]
        self.menWords = [ "men", "gentlemen", "gentlemen's", "gentlemens", "men's", "mens", "male", "masculine" ]
        
        ### additional words to filter gender-related information
        self.womenLemmas = [ "woman", "lady", "female", "feminine" ]
        self.menLemmas = [ "man", "gentleman", "male", "masculine" ]
    
        ### additional information to filter out    
        self.inWords = [ "in", "of", "and", "as", "at", "&amp;" ]
        self.theWords = [ "the", "a" ]
    
        
    ### gender functions
    
    def _isWomanTitle(self, title, words):
        return any([w in self.womenWords for w in words ])
    
    def _isManTitle(self, title, words):
        return any([w in self.menWords for w in words ])
    
    def _isGenderWord(self, word):
        return word in self.womenWords or word in self.menWords

    def _isGenderLemma(self, word):
        return word in self.womenLemmas or word in self.menLemmas
    
    def filterGenderInformation(self, words):
        result = [ w for w in words if not self._isGenderInfo(w) ]
        return result

    def getGeneralOptions(self, titleWords, lemmas):
        assert type(titleWords) == type([])
        assert type(lemmas) == type([])
        
        return [self.__removeInWomen(lemmas), 
                self.__removeInWomen(titleWords),
                self.__removeWomenS(lemmas),
                self.__removeWomenS(titleWords),
                self.filterGenderInformation(lemmas), 
                self.filterGenderInformation(titleWords) ]

    def __removeInWomen(self, words):
        result = [ ]
        
        for i, word in enumerate(words):
            if self._isGenderInfo(word):
                continue
            
            # removing "IN" for "Women in Politics"
            if word in self.inWords and i > 0 and self._isGenderInfo(words[i-1]):
                continue
            
            # removing "THE" for "Women in THE Politics"
            if word in self.theWords and i > 1 and words[i-1] in self.inWords and self._isGenderInfo(words[i-2]):
                continue
            
            result.append(word)
            
        return result
    
    def __removeWomenS(self, words):
        result = [ ]

        for i, word in enumerate(words):
            if self._isGenderInfo(word):
                continue
            
            # removing s for women 's
            if word == "s" and i > 0 and self._isGenderInfo(words[i-1]):
                continue
            
            result.append(word)
            
        return result
