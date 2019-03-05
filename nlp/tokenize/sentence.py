#!/usr/bin/env python
# -*-coding:utf-8-*-


from nltk.tokenize import sent_tokenize

from nlp.const import re_han_default


def sentence_tokenize(text, language='chinese'):
    """
    分句

    中文
    :param text:
    :return:
    """

    if language == 'chinese':
        re_han = re_han_default
        setenses = re_han.split(text)
        return setenses
    else:
        res = sent_tokenize(text, language=language)
        return res
