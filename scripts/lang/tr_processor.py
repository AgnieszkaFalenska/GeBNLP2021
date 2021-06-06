#!/usr/bin/env python

import projpath
from lang.lang_processor import LangProcessor

class TurkishLangProcessor(LangProcessor):
    def __init__(self):
        super().__init__("tr")
        self.catSteps = 0
        self.plNLP = None
        
        # gender words
        
        ### articles with this words will be filtered
        self.womenWords = [ "kadın", "kadınlar", "kadının", "kadınların", 
                            "kadını", "kadına", "kadında", "kadından", "kadının", "kadınla",
                            "kadınlar", "kadınları", "kadınlara", "kadınlarda", "kadınlardan", "kadınların", "kadınlarla",
                            "kadınını", "kadınına", "kadınında", "kadınından", "kadınının", "kadınıyla", "kadınları",
                            "kadınlarına", "kadınlarında", "kadınlarından", "kadınlarının", "kadınlarıyla", 
                            "bayanlar", "bayan" ]
                  
        self.menWords = [ "erkek", "erkekler", "erkeği", "erkeğe", "erkekte", "erkekten", 
                          "erkeğin", "erkekle",
                          "erkekler", "erkekleri", "erkeklere", "erkeklerde", "erkeklerden",
                          "erkeklerin", "erkeklerle", "erkeğini", "erkeğine", "erkeğinde",
                          "erkeğinden", "erkeğinin", "erkeğiyle", "erkekleri", "erkeklerine",
                          "erkeklerinde", "erkeklerinden", "erkeklerinin", "erkekleriyle",
                          "bay", "baylar" ]

        
        ### additional information to filter out
        self.andWords = [ "ve" ]
        self.inSuffix = [ "'de", "'da", "'te", "'ta", "de", "da", "te", "ta" ]
       
    ### gender functions
        
    def _isWomanTitle(self, title, words):
        return any([w in self.womenWords for w in words ])
    
    def _isManTitle(self, title, words):
        return any([w in self.menWords for w in words ])
    
    def _isGenderWord(self, word):
        return word in self.womenWords or word in self.menWords

    def _isGenderLemma(self, word):
        # no more info
        return False
    
    def filterGenderInformation(self, words):
        result = [ w for w in words if not self._isGenderInfo(w) ]
        return result

    def getGeneralOptions(self, titleWords, lemmas):
        assert type(titleWords) == type([])
        assert type(lemmas) == type([])
        
        return [self.__removeInWomen(lemmas), 
                self.__removeInWomen(titleWords),
                self.__removeWomenAnd(lemmas),
                self.__removeWomenAnd(titleWords),
                self.filterGenderInformation(lemmas), 
                self.filterGenderInformation(titleWords) ]

    def __removeInWomen(self, words):
        result = [ ]
        
        for i, word in enumerate(words):
            if self._isGenderInfo(word):
                continue
            
            # removing "TE" for "Xte kadın"
            suffs = [ s for s in self.inSuffix if word.endswith(s) ]
            if len(suffs) > 0 and i+1 < len(words) and self._isGenderInfo(words[i+1]):
                result.append(word[:-len(suffs[0])])
                continue
            
            result.append(word)
            
        return [ w for w in result if len(w) > 0 ]
    
    def __removeWomenAnd(self, words):
        result = [ ]

        for i, word in enumerate(words):
            if self._isGenderInfo(word):
                continue
            
            # removing "ve kadin" for women 's
            if word in self.andWords and i+1 < len(words) and self._isGenderInfo(words[i+1]):
                continue
            
            if word in self.andWords and i > 0 and self._isGenderInfo(words[i-1]):
                continue
                
            result.append(word)
            
        return result
