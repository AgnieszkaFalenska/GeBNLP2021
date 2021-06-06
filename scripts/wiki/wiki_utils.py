#!/usr/bin/env python

import sys, os
import json
import gzip, bz2


REDIRECT_TAG = "[REDIRECT]"
DISAMB_TAG = "[DISAMB]"
TEMPLATE_TAG = "[TEMPLATE]"
ARTICLE_TAG = "[ARTICLE]"
UNKNOWN_TAG = "[???]"

PAGE_TAG = "page"
SUBCAT_TAG = "subcat"

def __getFiles(dirName, result):
    for filename in os.listdir(dirName):
        fullPath = dirName + os.sep + filename
        if os.path.isfile(fullPath):
            result.append(fullPath)
        else:
            __getFiles(fullPath, result)

def getFiles(dirName):
    result = [ ]
    __getFiles(dirName, result)
    return result

try:
    from html import unescape  # python 3.4+
except ImportError:
    try:
        from html.parser import HTMLParser  # python 3.x (<3.4)
        unescape = HTMLParser().unescape
    except ImportError:
        unescape = None # python 2.x

try:
    from html import escape  # python 3.4+
except ImportError:
    try:
        from html.parser import HTMLParser  # python 3.x (<3.4)
        escape = HTMLParser().escape
    except ImportError:
        escape = None  # python 2.x
    
    
def openWikiFile(filename):
    if filename.endswith("gz"):
        infile = gzip.open(filename, "rt")
    elif filename.endswith("bz2"):
        infile = bz2.open(filename, "rt")
    else:
        infile = open(filename, "r")
        
    return infile


def getEscapePossibs(name):
    return [unescape(name), 
            escape(name), 
            unescape(name).replace("&", "&amp;"), 
            unescape(name).replace("'", "&#39;"), 
            unescape(name).replace('"', "&quot;")]
            
            