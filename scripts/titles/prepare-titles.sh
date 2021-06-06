#!/bin/bash

set -ue

D=$(readlink -f $(dirname ${BASH_SOURCE[0]}))
source $D/../get_global_vars.sh

LANG=$1

OUT_DIR=$INT_DIR/$LANG/titles
if [ ! -e $OUT_DIR ]; then
    mkdir -p $OUT_DIR
fi

WIKI_DIR=$INT_DIR/$LANG/wiki

$CMD/titles/filter_gender_titles.py $WIKI_DIR/wiki_articles_lemmas.txt $LANG $OUT_DIR/wiki_gender_titles.redirs.txt $WIKI_DIR/wiki_redirs.txt $WIKI_DIR/wiki_redirs_lemmas.txt

CAT_NAMES=$OUT_DIR/wiki_gender_titles.cats.txt
ARTICLE_NAMES=$OUT_DIR/wiki_gender_titles.articles.txt
$CMD/titles/prepare_title_categories.py $OUT_DIR/wiki_gender_titles.redirs.txt $WIKI_DIR/wiki_categories.txt $WIKI_DIR/wiki_article_cats.txt $WIKI_DIR/wiki_subcategories.txt $LANG $CAT_NAMES $ARTICLE_NAMES

$CMD/titles/filter_by_categories.py $WIKI_DIR/wiki_categories.txt $WIKI_DIR/wiki_article_cats.txt \
                                   $WIKI_DIR/wiki_subcategories.txt $OUT_DIR/wiki_gender_titles.redirs.txt $ARTICLE_NAMES $LANG $OUT_DIR/wiki_gender_titles.redirs.cats.txt
