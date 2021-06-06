#!/bin/bash

set -ue

D=$(readlink -f $(dirname ${BASH_SOURCE[0]}))
source $D/../get_global_vars.sh

LANG=$1
DUMP=$2

OUT_DIR=$INT_DIR/$LANG/wiki
if [ ! -e $OUT_DIR ]; then
    mkdir -p $OUT_DIR
fi

CONTENT=$DATA_DIR/$LANG/${LANG}wiki-$DUMP-pages-articles.xml.bz2
if [ ! -e $CONTENT ]; then
    echo "No content file", $CONTENT
    exit
fi

PAGES=$OUT_DIR/wiki_pages.txt
python $CMD/wiki/process_pages.py $CONTENT $LANG $PAGES
echo "Pages DONE"

REDIRS=$OUT_DIR/wiki_redirs.txt
python $CMD/wiki/process_redirs.py $PAGES $REDIRS
echo "Redirs DONE"

CATEGORIES_IN=$DATA_DIR/$LANG/${LANG}wiki-$DUMP-category.sql.gz
if [ ! -e $CATEGORIES_IN ]; then
    echo "No categories file", $CATEGORIES_IN
    exit
fi

CATEGORY_LINKS_IN=$DATA_DIR/$LANG/${LANG}wiki-$DUMP-categorylinks.sql.gz
if [ ! -e $CATEGORY_LINKS_IN ]; then
    echo "No category links file", $CATEGORY_LINKS_IN
    exit
fi

if [ $LANG == "en" ]; then
    ENC='ISO-8859-1'
else
    ENC="utf-8"
fi

CATEGORIES=$OUT_DIR/wiki_categories.txt
CATEGORY_LINKS=$OUT_DIR/wiki_categorylinks.txt
python $CMD/wiki/process_categories.py $CATEGORIES_IN $CATEGORY_LINKS_IN $CATEGORIES $CATEGORY_LINKS $ENC

SUBCATEGORIES=$OUT_DIR/wiki_subcategories.txt
SUBPAGES=$OUT_DIR/wiki_article_cats.txt
python $CMD/wiki/process_category_mapping.py $CATEGORIES $CATEGORY_LINKS $PAGES $SUBCATEGORIES $SUBPAGES

echo "Categories DONE"

LEMMAS=$OUT_DIR/wiki_articles_lemmas.txt
python $CMD/wiki/process_lemmas.py $PAGES $LANG $LEMMAS "[ARTICLE]" &

REDIR_LEMMAS=$OUT_DIR/wiki_redirs_lemmas.txt
python $CMD/wiki/process_lemmas.py $REDIRS $LANG $REDIR_LEMMAS &


wait
echo "Lemmas DONE"

