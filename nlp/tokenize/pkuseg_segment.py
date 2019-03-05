#!/usr/bin/env python
# -*-coding:utf-8-*-


from nltk.tokenize.api import TokenizerI
import pkuseg


class PkusegSegmenter(TokenizerI):
    """

    调用结巴分词

    """

    def __init__(self, *args, **kwargs):
        super(PkusegSegmenter, self).__init__(*args, **kwargs)
        self.seg = pkuseg.pkuseg()

    def tokenize(self, sentences):
        """
        核心分词接口方法
        """
        res = self.seg.cut(sentences)
        return res
