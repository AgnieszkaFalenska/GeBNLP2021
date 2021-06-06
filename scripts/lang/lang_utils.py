#!/usr/bin/env python

import string

def removePunctuation(word):
    puncts = string.punctuation
    puncts += "@“”’‘’‚‘"
    return "".join([ c for c in word if (c not in puncts) ])
    
def splitByPunctuation(word):
    puncts = string.punctuation
    puncts += "@“”’‘’"
    
    result = ""
    for c in word:
        if c in puncts:
            result += " " + c + " "
        else:
            result += c
            
    result = " ".join(result.strip().split())
    return result.split()
    
def loadSpacy(lang):
    import spacy
    
    if lang == "pl":
        nlp = spacy.load("pl_core_news_sm", disable=['parser', 'ner'])
    elif lang == "en":
        nlp = spacy.load("en_core_web_sm", disable=['parser', 'ner'])
    elif lang == "de":
        nlp = spacy.load("de_core_news_sm", disable=['parser', 'ner'])
    else:
        print("Unknown language code:", lang)
        sys.exit()
        
    nlp.add_pipe('sentencizer')
    return nlp
