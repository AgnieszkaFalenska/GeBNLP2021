#!/usr/bin/env python

import projpath
from lang.lang_processor import LangProcessor

class PolishLangProcessor(LangProcessor):
    def __init__(self):
        super().__init__("pl")
        self.catSteps = 1

        # gender words
        
        ### articles with this words will be filtered
        self.womenWords = set(["kobiety", "kobiet", "kobietom", "kobiety", "kobietami", "kobietach", "kobiety", #women
                           "kobiecy", "kobiecego", "kobiecemu", "kobiecym",                                 #female
                           "kobieca", "kobiecej", "kobiecą", "kobiece", "kobiecych",
                           "żeński", "żeńskiego", "żeńskiemu", "żeńskim",                                   #feminine
                           "żeńska", "żeńskiej", "żeńską", "żeńskie", "żeńskich",
                           "damski", "damskiego", "damskiemu", "damskim",
                           "damska", "damskiej", "damską", "damskie", "damskich" ])
                           
        self.menWords = set(["mężczyźni", "mężczyzn", "mężczyznom", "mężczyzn", "mężczyznami", "mężczyznach",   # men
                         "męski", "męskiego", "męskiemu", "męskim",                                         #male
                         "męska", "męskiej", "męską", "męskie", "męskich" ])
        
        ### additional words to filter gender-related information
        self.womenLemmas = set(["kobieta", "damski", "kobiecy", "żeński"])
        self.menLemmas = set(["mężczyzna", "męski"])
        
        ### additional information to filter out
        self.inWords =  [ "w", "i", "do", "nad", "na" ]
        
    ## gender functions
    
    def _isWomanTitle(self, title, words):
        return any([w in self.womenWords for w in words ])
    
    def _isManTitle(self, title, words):
        return any([w in self.menWords for w in words ])

    def _isGenderWord(self, word):
        return word in self.womenWords or word in self.menWords

    def _isGenderLemma(self, lemma):
        return lemma in self.womenLemmas or lemma in self.menLemmas
    
    def filterGenderInformation(self, words):
        result = [ w for w in words if not self._isGenderInfo(w) ]
        return result

    def getGeneralOptions(self, titleWords, lemmas):
        assert type(titleWords) == type([])
        assert type(lemmas) == type([])
        
        return [self.__removeInWomen(lemmas), self.__removeInWomen(titleWords), 
                self.filterGenderInformation(lemmas), 
                self.filterGenderInformation(titleWords) ]
    
    def __removeInWomen(self, words):
        # add option without "IN" for "Women in Politics"
        result = [ ]
        for i, word in enumerate(words):
            if self._isGenderInfo(word):
                continue
            
            if word in self.inWords and i > 0 and self._isGenderInfo(words[i-1]):
                continue
                
            result.append(word)
           
        return result

