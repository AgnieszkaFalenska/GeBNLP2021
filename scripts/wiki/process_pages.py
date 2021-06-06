#!/usr/bin/env python

import sys, os
import json
import gzip, bz2
import re, codecs
import wiki_lang
from wiki_utils import *

def processPage(pageId, title, redirectTitle, content, lang, out):
    disambiguation = lang.isDisambiguationPage(title, content)
    
    titleWords = title.split()
    if disambiguation:
        tag = DISAMB_TAG
    elif len(titleWords) > 0 and ":" in titleWords[0]:
        tag = TEMPLATE_TAG
    elif redirectTitle is not None:
        tag = REDIRECT_TAG
        title = "[" + title.strip() + "]|[" + redirectTitle.strip() + "]" 
    else:
        tag = ARTICLE_TAG
        
    out.write(pageId + "\t" + tag + "\t" + str(title) + "\n")
    
def processPages(inFile, lang, out):
    infile = openWikiFile(inFile)
    
    title = None
    pageId = None
    redirect = None
    
    pageContent = None
    inText = None
    for line in infile:
        line = line.strip()
        
        if "<text" in line:
            pageContent = [ line ]
            inText = True
        elif inText:
            pageContent.append(line)
            
        if "</text>" in line:
            if len(pageContent) > 1:
                pageContent.append(line)
                
            inText = False
            
        
        if "</page>" in line:
            processPage(pageId, title, redirect, "\n".join(pageContent), lang, out)
            title = None
            pageId = None
            redirect = None
            pageContent = None
            inText = None
        elif "<title>" in line:
            title = line.split("<title>")[1].split("</title>")[0]
        elif "<id>" in line and pageId is None:
            pageId = line.split("<id>")[1].split("</id>")[0]
        elif "<redirect title" in line:
            redirect = line.split("title=")[1].split("/>")[0].strip()
            if redirect.startswith('"'):
                redirect = redirect[1:]
                
            if redirect.endswith('"'):
                redirect = redirect[:-1]
         
if __name__ == "__main__":
    # plwiki-20210301-pages-articles.xml.bz2
    articlesFilename = sys.argv[1]

    # lang code
    lang = wiki_lang.buildLangProcessor(sys.argv[2])
    
    # intermediate-data/pl/wiki/wiki_articles.txt
    out = open(sys.argv[3], "w")

    processPages(articlesFilename, lang, out)
