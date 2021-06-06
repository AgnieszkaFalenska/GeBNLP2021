#!/usr/bin/env python

import sys

from lang.en_processor import EnglishLangProcessor
from lang.pl_processor import PolishLangProcessor
from lang.de_processor import GermanLangProcessor
from lang.tr_processor import TurkishLangProcessor

def buildLangProcessor(lang):
    if lang == "pl":
        return PolishLangProcessor()
    elif lang == "en":
        return EnglishLangProcessor()
    elif lang == "de":
        return GermanLangProcessor()
    elif lang == "tr":
        return TurkishLangProcessor()
    
    print("Unknown language code:", lang)
    sys.exit()
    
