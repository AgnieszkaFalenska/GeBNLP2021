#!/usr/bin/env python

import projpath
import os
from lang.lang_processor import LangProcessor

class GermanLangProcessor(LangProcessor):
    def __init__(self):
        super().__init__("de")
        self.catSteps = 0
        self.prefixWenderWords = None
        
        # gender words
        
        ### articles with this words will be filtered
        self.womenWords = ["frauen", "damen",                                                  # women 
                           "weibliche", "weibliches", "weiblich", "weiblicher", "weiblichen" ] # female
        
        self.menWords = ["männer", "herren", 
                         "männliche", "männliches", "männlich", "männlicher", "männlichen" ]
        
        self.womenSuffixes = [ "innen" ]
        self.menAddSuffixes = [ "", "e", "n", "en", "schaft" ]
        
        ### additional words to filter gender-related information
        self.womenLemmas = [ "frau", "dame", "weiblich" ]
        self.menLemmas = [ "mann", "herr", "männlich" ]
        
        ### additional information to filter out    
        self.inWords = [ "in", "im", "für", "und", "nach", "gegen" ]
        self.derWords = [ "der", "die", "den", "dem" ]
        self.genderInfo = [ (len(w), w) for w in self.womenWords + self.menWords + self.womenLemmas + self.menLemmas ]
        self.genderInfo.sort(reverse=True)
        
    ### gender functions
        
    def _isWomanTitle(self, title, words):
        for i, w in enumerate(words):
            if any([w.startswith(ww) for ww in self.womenWords ]) and self._isGenderWord(w):
                return True
                
            if any([w.endswith(ww) for ww in self.womenSuffixes ]) and self._isGenderWord(w):
                if len(words) < 2:
                    return False
                
                shorter = self.__removeGenderInfo(w, "")    
                if any([shorter+suff in words for suff in self.menAddSuffixes ]):
                    return False
                
                if "Innen" in title:
                    return False
                
                if w + "- und" in title.lower() or w + " und -" in title.lower():
                    return False
                
                    
                if i == 0 and words[1] in [ "der", "von", "vom" ]:
                    return False
                    
                return True
                
        return False
    
    def _isManTitle(self, title, words):
        for w in words:
            if any([w.startswith(ww) for ww in self.menWords ]) and self._isGenderWord(w):
                return True
                
        return False

    def _isGenderWord(self, word):
        return self.__isFullGenderWord(word) or self.__isPrefixGenderWord(word) or self.__isSuffixGenderWord(word)
  
    def _isGenderLemma(self, word):
        return word in self.womenLemmas or word in self.menLemmas
    
    def filterGenderInformation(self, words, addSuff=""):
        result = [ self.__removeGenderInfo(l, addSuff) for l in words ]
        return [ r for r in result if len(r) > 0 ]
    
    def getGeneralOptions(self, titleWords, lemmas):
        assert type(titleWords) == type([])
        assert type(lemmas) == type([])
        
        result = [ ]
        for suff in self.menAddSuffixes:
            result += [ self.__removeWomenIm(titleWords, addSuff=suff), 
                        self.__removeWomenIm(lemmas, addSuff=suff),  
                        self.__removeWomenDer(titleWords, addSuff=suff), 
                        self.__removeWomenDer(lemmas, addSuff=suff),
                        self.__removeImWomen(titleWords, addSuff=suff), 
                        self.__removeImWomen(lemmas, addSuff=suff),
                        self.filterGenderInformation(lemmas, addSuff=suff), 
                        self.filterGenderInformation(titleWords, addSuff=suff) ]
    
        return result
        
    def __isFullGenderInfo(self, word):
        return self.__isFullGenderWord(word) or self._isGenderLemma(word)
        
    def __removeGenderInfo(self, word, addSuff):
        if not self._isGenderInfo(word):
            return word
        
        if self.__isFullGenderInfo(word):
            return ""
        
        for _, gi in self.genderInfo:
            if word.startswith(gi):
                return word[len(gi):]
              
        for sf in self.womenSuffixes:
            if word.endswith(sf):
                result = word[:-len(sf)]
                result += addSuff
                
                return result
                
        # should not get here
        return None
                

    def __isFullGenderWord(self, word):
        return word in self.womenWords + self.menWords
        
    def __isPrefixGenderWord(self, word):
        if self.prefixWenderWords is None:
            thisFile = os.path.realpath(__file__)
            thisPath = os.path.dirname(thisFile)
            self.prefixWenderWords = set([ w.strip() for w in open(thisPath + "/de.gender_words.txt", "r")])

        return word in self.prefixWenderWords

    def __isSuffixGenderWord(self, word):
        return self.__isPrefixGenderWord(word)
                        
    def __removeWomenDer(self, words, addSuff):
        result = [ ]
        
        for i, w in enumerate(words):
            if self.__isFullGenderInfo(w):
                continue
                
            if any([w.endswith(ww) for ww in self.womenSuffixes ]) and self.__isSuffixGenderWord(w):
                w = self.__removeGenderInfo(w, addSuff)
                
            # removing "der" for "der Frauen"
            if w in self.derWords and i < len(words) and self.__isFullGenderInfo(words[i+1]):
                continue
                    
            result.append(w)
            
        return result

    def __removeWomenIm(self, words, addSuff):
        result = [ ]
        
        for i, w in enumerate(words):
            if self.__isFullGenderInfo(w):
                continue
                
            if any([w.endswith(ww) for ww in self.womenSuffixes ]) and self.__isSuffixGenderWord(w):
                w = self.__removeGenderInfo(w, addSuff)
                
            # removing "im" for "Frauen im Militär"
            if w in self.inWords and i > 0 and self.__isFullGenderInfo(words[i-1]):
                continue
            
            # removing "der" for "Frauen in der Bibel"
            if w in self.derWords and i > 1 and words[i-1] in self.inWords and self.__isFullGenderInfo(words[i-2]):
                continue
            
            result.append(w)
            
        return result
        
    def __removeImWomen(self, words, addSuff):
        result = [ ]
        
        for i, w in enumerate(words):
            if self.__isFullGenderInfo(w):
                continue
                
            if any([w.endswith(ww) for ww in self.womenSuffixes ]) and self.__isSuffixGenderWord(w):
                w = self.__removeGenderInfo(w, addSuff)
                
            # removing "gegen" for "Gewalt gegen Frauen"
            if w in self.inWords and i+1 < len(words) and self.__isFullGenderInfo(words[i+1]):
                continue
            
            result.append(w)
            
        return result
