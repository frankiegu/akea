#!/usr/bin/env python
# -*-coding:utf-8-*-


from nltk.tokenize.api import TokenizerI
import jieba


class JiebaSegmenter(TokenizerI):
    """

    调用结巴分词

    """

    def __init__(self, *args, **kwargs):
        super(JiebaSegmenter, self).__init__(*args, **kwargs)

    def tokenize(self, sentences):
        """
        核心分词接口方法
        """
        res = jieba.lcut(sentences)
        return res
