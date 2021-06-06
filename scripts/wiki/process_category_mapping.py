#!/usr/bin/env python

#import spacy
import sys, os
import json
import logging
import re, codecs
import wiki_utils

def readCategories(categoriesFilename):
    cats = { }
    for line in open(categoriesFilename, "r"):
        catId, catName = line.strip().split('\t')
        cats[catName] = catId
    return cats

def readArticles(articlesFilename):
    articles = { }
    for line in open(articlesFilename):
        words = line.strip().split('\t')
        
        articleId = words[0]
        articleTitle = words[2]
        
        if articleId in articles:
            logging.error("Twice the same ID: %s" % articleId)
            sys.exit()
        
        articles[articleId] = articleTitle
    return articles

def mapArticleToCategory(articleTitle, categories):
    def __cleanCategoryName(catName):
        catName = "_".join(catName.split())

        if ":" in catName:
            catName = ":".join(catName.split(":")[1:])

        catName = wiki_utils.unescape(catName)
        catName = catName.replace("'", "\\'")
        catName = catName.replace('"', '\\"')
        return catName
    
    articleCatName = __cleanCategoryName(articleTitle)
    if articleCatName not in categories:
        logging.warning("Unknown mapping to category: %s" % articleCatName)
        return None
    else:
        return categories[articleCatName]
                
def categoryLinksToIds(categories, articles, articleCatsFilename, outCat, outPage):
    articleCats = { }
    subCats = { }
    for line in open(articleCatsFilename):
        articleId, catId, catType = line.strip().split('\t')
    
        if articleId not in articles:
            # the file is full of non-existing articles
            continue

        if catType == "page":
            articleCats.setdefault(int(articleId), [ ])
            articleCats[int(articleId)].append(catId)
        else:
            articleTitle = articles[articleId]
            fromCatId = mapArticleToCategory(articleTitle, categories)
            
            if fromCatId is None:
                continue
                
            subCats.setdefault(int(fromCatId), [ ])
            subCats[int(fromCatId)].append(catId)

    for (articleId, articleCats) in sorted(articleCats.items()):
        outPage.write(str(articleId) + '\t' + ','.join(articleCats) + "\n")

    for (catId, catCats) in sorted(subCats.items()):
        outCat.write(str(catId) + '\t' + ','.join(catCats) + "\n")

if __name__ == "__main__":
    categoriesFilename = sys.argv[1]
    categoryLinksFilename = sys.argv[2]
    articlesFilename = sys.argv[3]
    
    subcategories = sys.argv[4]
    catpages = sys.argv[5]
    
    categories = readCategories(categoriesFilename)
    logging.info("Nr of categories: %i" % len(categories))
    
    articles = readArticles(articlesFilename)
    logging.info("Nr of articles: %i" % len(articles))
    
    categoryLinksToIds(categories, articles, categoryLinksFilename, open(subcategories, "w"), open(catpages, "w"))
