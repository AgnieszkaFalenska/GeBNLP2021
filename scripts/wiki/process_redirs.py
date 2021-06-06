#!/usr/bin/env python

#import spacy
import sys, os
import json
import gzip, bz2
import re, codecs
import logging
from wiki_utils import *

def extendRedirectedTitles(possibs, redirs):
    added = [ ]
    for possib in possibs:
        if possib in redirs:
            _, _, origTitle = redirs[possib]
            if origTitle not in possibs:
                added.append(origTitle)
    
    possibs |= set(added)
    if len(added) > 0:
        extendRedirectedTitles(possibs, redirs)
    
def processRedirs(filename, out):
    allArticles = { }
    
    redirectTitles = { }
    for line in open(filename, "r"):
        words = line.strip().split('\t')
        
        articleId = int(words[0])
        articleType = words[1]
        title = words[2]
        
        if title in allArticles:
            logging.warning("Two articles with the same title: %s %i %i" % (title, articleId, allArticles[title][0]))
            continue

        allArticles[title] = (articleId, articleType)
        
        if articleType == REDIRECT_TAG:
            title = title[1:-1]
            redirectTitle, origTitle = title.split("]|[")
            
            if redirectTitle in redirectTitles:
                logging.warning("Two redirects with the same title: %s %i %i" % (redirectTitle, articleId, redirectTitles[redirectTitle][0]))
                continue
        
            redirectTitles[redirectTitle] = (articleId, articleType, origTitle)
        
    result = [ ]
    for redirectTitle, (articleId, articleType, origTitle) in redirectTitles.items():
        #redirectTitle, origTitle = title.split("|")
        
        origId = -1
        origType = "[???]"
                
        if origTitle in allArticles:
            origId, origType = allArticles[origTitle]
        else:
            # there is tons of different options
            titlePossibs = set([origTitle,
                            unescape(origTitle), 
                            escape(origTitle), 
                            unescape(origTitle).replace("&", "&amp;"), 
                            unescape(origTitle).replace("'", "&#39;"),
                            unescape(origTitle).replace('"', "&quot;")])
            
            extendRedirectedTitles(titlePossibs, redirectTitles)
                
            for possib in titlePossibs:
                if possib in allArticles:
                    origId, origType = allArticles[possib]
                    break
        
        if origId == -1:
            logging.warning("Didn't find page for redirection: %s %s %i" % (redirectTitle, origTitle, articleId))
            
        result.append((articleId, redirectTitle, origId, origType))
        
    for (articleId, redirectTitle, origId, origType) in sorted(result):
        toWrite = [ str(articleId), REDIRECT_TAG, redirectTitle, str(origId), origType ]
        out.write('\t'.join(toWrite) + "\n")
        
if __name__ == "__main__":
    # intermediate-data/pl/wiki/wiki_articles.txt
    articlesFilename = sys.argv[1]

    # intermediate-data/pl/wiki/wiki_articles_with_redirs.txt
    outFile = sys.argv[2]

    processRedirs(articlesFilename, open(outFile, "w"))
    
    