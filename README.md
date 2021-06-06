# GeBNLP2021

This repository contains all the scripts and data used in the paper Assessing Gender Bias in Wikipedia: Inequalities in Article Titles, accepted at the [3rd Workshop on Gender Bias in Natural Language Processing](https://genderbiasnlp.talp.cat/).

## Usage

### Download Wikipedia

The first step is to manually download the desired Wikipedia dump and put it into the data/$LANG folder. Three files are requires:
* ${LANG}wiki-$DUMP-pages-articles.xml.bz2
* ${LANG}wiki-$DUMP-category.sql.gz
* ${LANG}wiki-$DUMP-categorylinks.sql.gz

### Prepare stats

When the Wikipedia files are in place, then run:

```sh
wiki/prepare-wiki.sh $LANG $DUMP
titles/prepare-titles.sh $LANG
stats/prepare-paper-data.sh $LANG
```

The process will take a while (especially the first step and processing Wikipedia files). The files with title statistics will be created in the directory for_paper/$DATE
