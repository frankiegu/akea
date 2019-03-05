#!/usr/bin/env python
# -*-coding:utf-8-*-

from nltk.corpus.util import LazyCorpusLoader

from nlp.corpus.reader.plaintext import ZhPlaintextCorpusReader

zh_novel = LazyCorpusLoader(
    'zh_novel', ZhPlaintextCorpusReader, r'(?!\.).*\.txt', encoding='utf8'
)
