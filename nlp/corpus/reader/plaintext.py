#!/usr/bin/env python
# -*-coding:utf-8-*-


from nltk.corpus.reader.plaintext import *

from nlp.tokenize.jieba_segment import JiebaSegmenter
from nlp.tokenize.pkuseg_segment import PkusegSegmenter


class ZhPlaintextCorpusReader(PlaintextCorpusReader):
    """
    继承自PlaintextCorpusReader 专门针对中文的定制

    中文分词接口


    """

    CorpusView = StreamBackedCorpusView
    """The corpus view class used by this reader.  Subclasses of
       ``PlaintextCorpusReader`` may specify alternative corpus view
       classes (e.g., to skip the preface sections of documents.)"""

    def __init__(
            self,
            root,
            fileids,
            word_tokenizer=PkusegSegmenter(),
            sent_tokenizer=RegexpTokenizer(r'。|？|！'),
            para_block_reader=read_blankline_block,
            encoding='utf8',
    ):
        """
        Construct a new plaintext corpus reader for a set of documents
        located at the given root directory.  Example usage:

            >>> root = '/usr/local/share/nltk_data/corpora/webtext/'
            >>> reader = PlaintextCorpusReader(root, '.*\.txt') # doctest: +SKIP

        :param root: The root directory for this corpus.
        :param fileids: A list or regexp specifying the fileids in this corpus.
        :param word_tokenizer: Tokenizer for breaking sentences or
            paragraphs into words.
        :param sent_tokenizer: Tokenizer for breaking paragraphs
            into words.
        :param para_block_reader: The block reader used to divide the
            corpus into paragraph blocks.
        """
        CorpusReader.__init__(self, root, fileids, encoding)
        self._word_tokenizer = word_tokenizer
        self._sent_tokenizer = sent_tokenizer
        self._para_block_reader = para_block_reader
