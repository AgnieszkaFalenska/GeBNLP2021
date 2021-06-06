#!/usr/bin/env python

#import spacy
import sys
import re, gzip
import wiki_utils
import logging
import codecs

def findCategoryId(catName, catIds):
    if catName in catIds:
        return catIds[catName]
    
    possibs = wiki_utils.getEscapePossibs(catName)
    for possib in possibs:
        if possib in catIds:
            return catIds[possib]
                    
    logging.warning("Unknown category: %s" % catName)
    return None
    
def convertName(name, encoding):
    try:
        return name.encode(encoding).decode("utf-8")
    except:
        try:
            return name.encode("utf-8").decode("utf-8")
        except:
            print("No idea what to do with this:", name)
            return name
            
def processCategoryIds(inFilename, out, encoding):
    infile = gzip.open(inFilename, "rt", encoding=encoding)
    
    patt = "\((\d+),'([^']*(?:\\'[^']*)*?)',-?\d+,-?\d+,-?\d+\)"
    
    catIds = { }
    for line in infile:
        for match in re.finditer(patt, line):
            catId = match.group(1)
            catName = convertName(match.group(2), encoding)
            
            if catName in catIds:
                logging.warning("Category already stored: %s" % catName)
            else:
                catIds[catName] = catId
                out.write(catId + '\t' + catName + "\n")
    
    return catIds

def processCategoryLinks(inFilename, catIds, out):
    infile = gzip.open(inFilename, "rt", encoding='ISO-8859-1')
        
    #([^']*(?:\\'[^']*)?)
    patt = "\((\d+),'([^']*(?:\\'[^']*)*?)','.*?','.*?','.*?','.*?','(.*?)'\)"
    for line in infile:
        matches = list(re.finditer(patt, line))
        for match in matches:
            # filtering links to files etc.
            if match.group(3) not in [ wiki_utils.PAGE_TAG, wiki_utils.SUBCAT_TAG]:
                continue
            else:
                articleId = match.group(1)
                catName = match.group(2).encode("ISO-8859-1").decode("utf-8")
                linkType = match.group(3)
                
                catId = findCategoryId(catName, catIds)
                toWrite = [ articleId, str(catId), linkType ]
                out.write('\t'.join(toWrite) + "\n")
       

if __name__ == "__main__":
    categories = sys.argv[1]
    categoryLinks = sys.argv[2] 
     
    outCategories = sys.argv[3]
    outCategoryLinks = sys.argv[4]
    
    encoding = "utf-8"
    if len(sys.argv) > 5:
        encoding = 'ISO-8859-1'
        
    catIds = processCategoryIds(categories, open(outCategories, "w"), encoding)
    logging.info("Nr of categories: %i" % len(catIds))
    processCategoryLinks(categoryLinks, catIds, open(outCategoryLinks, "w"))
    