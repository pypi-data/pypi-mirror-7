#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division, print_function, unicode_literals)

"""all about transform"""


import sys
import copy
import re
import string
from .corpus import Corpus
from .helper import MLStripper


def get_transformations():
    return ["to_lower", "remove_numbers", "remove_latin_punctuations", "remove_unicode_punctuations",
      "remove_latin_words", "remove_cjk_words", "remove_html_tags", "strip_whitespaces"]


def to_lower(s):
    """convert string to lowercase and return the result"""
    return s.lower()


def strip_whitespaces(s):
    """shrink mutiple whitespaces into a whitespaces"""
    s = " ".join(s.split())
    return s


def remove_numbers(s):
    """remove all the numbers/digits."""
    s = "".join([i for i in s if not i.isdigit()])
    return s


def remove_latin_punctuations(s):
    """remove latin punctuations"""
    #workaround
    #table = string.maketrans("","")
    #return s.translate(table, string.punctuation)
    remove_punctuation_map = dict((ord(char), u' ') for char in string.punctuation)
    return s.translate(remove_punctuation_map)


def remove_unicode_punctuations(s):
    """remove all unicode punctuations, slow!!!!"""
    tbl = dict.fromkeys([i for i in xrange(sys.maxunicode)
                      if unicodedata.category(unichr(i)).startswith('P')], u' ')
    #TODO maybe a global variable or take it in a file is better
    return s.translate(tbl)
    # import regex
    # return regex.sub(ur"\p{P}+", "", s)


def remove_html_tags(html):
    s = MLStripper()
    s.feed(html)
    return s.get_data()


def remove_latin_words(s, words, encoding="utf-8"):
    """
    Find the words and remove them, latin words only.
    Side effect: it would remove all the extra wihte spaces too!!!!

    Prameters
    ==========
    s: a string.
        For example, u'i am feeling good now'.
    words: a list of latin words to be removed.
        For example, ["now", "i"]
    encoding: encoding, defaultly "utf-8"
        The encoding of s.

    Returns
    =======
    result: a string with words and extra whitespaces removed (side effect).
        For example, u'am feeling good'

    """
    #slower
    #tmp = re.compile(r'\b%s\b' % r'\b|\b'.join(map(re.escape, words)))
    #return tmp.sub("", s)
    #TODO remove side effect
    result = " ".join([i for i in s.split() if not i in words])
    return result


def remove_cjk_words(s, words, encoding="utf-8"):
    """
    (Experiment.)
    Find the words and remove them, CJK words only.
    CJK words mean Chinese, Japanese, and Korean words.
    They are different from latin words that they are not seperated by whitespaces!!
    Attention: s and words should use the same encoding.

    s: a string.
        For example, u'你好，这个世界很温柔。'.
    words: a list of latin words to be removed.
        For example, ["你好", "这", "个"]
    encoding: encoding, defaultly "utf-8"
        The encoding of s.

    Returns
    =======
    result: a string with words and extra whitespaces removed (side effect).
        For example, u"，世界很温柔。"

    """
    #TODO effectiver ways
    words.sort(key=len)
    words.reverse() # find the longeer ones then the shorter ones
    for word in words:
        s = re.sub(word, "", s)
    return s
