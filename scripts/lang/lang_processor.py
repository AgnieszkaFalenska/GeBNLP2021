#!/usr/bin/env python

from abc import ABCMeta, abstractmethod
from lang.lang_utils import removePunctuation
from lang.cat_processor import CatProcessor

class LangProcessor(metaclass=ABCMeta):
        
    def __init__(self, lang):
        self.lang = lang
        self.catProcessor = CatProcessor(lang)
        self.nlp = None
        
        self.wikiContentDisamb = [ "{{disambiguation}}", "{{ujednoznacznienie}}", "{{begriffsklärung}}", "{{anlam ayrımı}}" ]
        self.wikiTitleDisamb = [ "(disambiguation)", "(ujednoznacznienie)", "(begriffsklärung)", "(anlam ayrımı)" ] 
        
        self.catSteps = None
        self.matchSteps = 3
        self.genderSteps = 5
                            
    # main functions
    
    def lemmatize(self, text):
        if self.nlp is None:
            self.nlp = loadSpacy(self.lang)
            
        doc = self.nlp(text)
        return [ t.lemma_ for t in doc ]

    
    ### page functions
    
    def isDisambiguationPage(self, title, content):
        return any([t in title.lower() for t in self.wikiTitleDisamb]) or any([c in content.lower() for c in self.wikiContentDisamb])
    
    # gender functions
    
    def isGenderedCategory(self, catName):
        assert type(catName) == type("")
        
        words = [ removePunctuation(w.lower()) for w in catName.split("_") ]
        words = [ w for w in words if len(w) > 0 ]
        return any([self._isGenderInfo(w) for w in words ])
    
    def isLangWomanTitle(self, title, titleWords, lemmaWords):
        return self._isWomanTitle(title, titleWords)
        
        
    def isLangManTitle(self, title, titleWords, lemmaWords):
        return self._isManTitle(title, titleWords)
    
    def _isGenderInfo(self, word):
        return self._isGenderWord(word) or self._isGenderLemma(word)
    
    @abstractmethod
    def _isWomanTitle(self, words):
        pass
    
    @abstractmethod    
    def _isManTitle(self, words):
        pass
    
    @abstractmethod
    def _isGenderLemma(self, word):
        pass
    
    @abstractmethod
    def _isGenderWord(self, word):
        pass
        
    @abstractmethod
    def filterGenderInformation(self, words):
        pass
        
    @abstractmethod
    def getGeneralOptions(self, title, lemmas):
        pass
