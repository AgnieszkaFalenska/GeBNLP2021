#!/usr/bin/env python

import sys
import wiki_lang

# add lemmas to regular titles 
def lemmatizeTitles(filename, lang, out, backLemmas, filterTag=None):
    for line in open(filename, "r"):
        words = line.strip().split('\t')
        
        articleId = words[0]
        articleType = words[1]
        title = words[2]
        
        if filterTag is not None and articleType != filterTag:
            continue
        
        if title in backLemmas:
            lemmas = backLemmas[title]
        else:
            lemmas = " ".join(lang.lemmatize(title))
            
        out.write(articleId + '\t' + title + '\t' + lemmas + '\n')
    
if __name__ == "__main__":
    titlesFilename = sys.argv[1]
    lang = wiki_lang.buildLangProcessor(sys.argv[2])
    out = open(sys.argv[3], "w")
    
    filterTag = None
    if len(sys.argv) > 4:
        filterTag = sys.argv[4]
        
    backLemmas = { }
    if len(sys.argv) > 5:
        for line in open(sys.argv[5]):
            _, title, lemmas = line.strip().split('\t')
            backLemmas[title] = lemmas
    print("Size of back lemmas", len(backLemmas))
    
    lemmatizeTitles(titlesFilename, lang, out, backLemmas, filterTag)
    
    
