#!/usr/bin/env python
# -*-coding:utf-8-*-

import re
import math
import threading
import logging
import os
import time
from hashlib import md5
import tempfile
import marshal

from .utils import normalized_path
from .hmm import cut as hmm_cut

from .compat import _replace_file
from .utils import strdecode, get_module_res

from mymodule.utils.path_utils import get_project_path
from nlp.const import DEFAULT_DICT, DEFALUT_CACHE_NAME, CATERING_DICT, re_eng, re_han_default, re_skip_default, \
    re_userdict

DICT_WRITING = {}

logger = logging.getLogger(__name__)


def resolve_filename(f):
    try:
        return f.name
    except AttributeError:
        return repr(f)


default_new_word_find = hmm_cut


class Segment():
    def __init__(self, dictionary=None, load_catering_dict=True, with_pos=False):
        """

        load_catering_dict 是否加载餐饮专业领域词典 默认加载
        with_pos 返回结果是否包含词性标注 默认不包含词性

        :param dictionary:
        :param load_catering_dict:
        :param with_pos:
        """
        self.lock = threading.RLock()

        if dictionary is None:
            self.dictionary = self.get_default_dict()
        else:
            self.dictionary = normalized_path(dictionary)

        self.load_catering_dict = load_catering_dict  # 是否加载catering行业字典

        self.FREQ = {}
        self.total = 0
        self.user_word_tag_tab = {}
        self.initialized = False
        self.tmp_dir = None
        self.cache_file = None

    def get_default_dict(self):
        return os.path.join(get_project_path('dicts'), DEFAULT_DICT)

    def get_catering_dict(self):
        return os.path.join(get_project_path('dicts'), CATERING_DICT)

    def get_catering_dictfile(self):
        return open(self.get_catering_dict(), 'rb')

    def gen_pfdict(self, f):
        lfreq = {}
        ltotal = 0

        f_name = resolve_filename(f)

        for lineno, line in enumerate(f):
            try:
                line = line.strip().decode('utf-8')

                if len(line) > 2:
                    word, freq = line.split(' ')[:2]
                elif len(line) == 2:
                    word, freq = line.split(' ')
                elif len(line) == 1:
                    word = line
                    freq = 1
                else:
                    logger.warning(f'{line} passed')

                freq = int(freq)
                lfreq[word] = freq
                ltotal += freq

            except ValueError:
                raise ValueError('invalid dictionary entry in {0} at Line {1}: {2}'.format(f_name, lineno, line))
        f.close()
        return lfreq, ltotal

    def merge_freq(self, freq1, freq2):
        freq = freq1.copy()
        for k, v in freq2.items():
            if k in freq:
                freq[k] += v
            else:
                freq[k] = v

        return freq

    def initialize(self, dictionary=None):
        if dictionary:
            abs_path = normalized_path(dictionary)
            if self.dictionary == abs_path and self.initialized:
                return
            else:
                self.dictionary = abs_path
                self.initialized = False
        else:
            abs_path = self.dictionary

        with self.lock:  # 字典在建造时的线程锁
            if self.initialized:  # 已经初始化了就不用初始化了
                return

            logging.debug("Building prefix dict from %s ..." % (abs_path or 'the default dictionary'))
            t1 = time.time()

            if self.cache_file:
                cache_file = self.cache_file

            # default dictionary
            elif abs_path == self.get_default_dict() and not self.load_catering_dict:  # 行业字典若要加载也进入这里的缓存
                cache_file = DEFALUT_CACHE_NAME
            elif abs_path == self.get_default_dict() and self.load_catering_dict:
                cache_file = 'segment_catering.cache'
            # custom dictionary
            else:
                cache_file = "segment.{0}.cache".format(md5(abs_path.encode('utf-8', 'replace')).hexdigest())

            cache_file = os.path.join(self.tmp_dir or tempfile.gettempdir(), cache_file)
            tmpdir = os.path.dirname(cache_file)

            load_from_cache_fail = True
            if os.path.isfile(cache_file) and (abs_path == DEFAULT_DICT or
                                               os.path.getmtime(cache_file) > os.path.getmtime(abs_path)):
                logging.debug("Loading model from cache {0}".format(cache_file))
                try:
                    with open(cache_file, 'rb') as cf:
                        self.FREQ, self.total = marshal.load(cf)
                    load_from_cache_fail = False
                except Exception:
                    load_from_cache_fail = True

            if load_from_cache_fail:
                wlock = DICT_WRITING.get(abs_path, threading.RLock())
                DICT_WRITING[abs_path] = wlock
                with wlock:
                    self.FREQ, self.total = self.gen_pfdict(self.get_dict_file())

                    if self.load_catering_dict:
                        self.FREQ2, self.total2 = self.gen_pfdict(self.get_catering_dictfile())

                        self.FREQ = self.merge_freq(self.FREQ, self.FREQ2)
                        self.total += self.total2

                    logging.debug("Dumping model to file cache {0}".format(cache_file))
                    try:
                        # prevent moving across different filesystems
                        fd, fpath = tempfile.mkstemp(dir=tmpdir)
                        with os.fdopen(fd, 'wb') as temp_cache_file:
                            marshal.dump((self.FREQ, self.total), temp_cache_file)
                        _replace_file(fpath, cache_file)
                    except Exception:
                        logging.exception("Dump cache file failed.")

                try:
                    del DICT_WRITING[abs_path]
                except KeyError:
                    pass

            self.initialized = True
            logging.debug("Loading model cost %.3f seconds." % (time.time() - t1))
            logging.debug("Prefix dict has been built succesfully.")

    def check_initialized(self):
        if not self.initialized:
            self.initialize()

    def get_DAG(self, sentence):
        self.check_initialized()

        DAG = {}
        N = len(sentence)
        for k in range(N):
            tmplist = []
            i = k
            frag = sentence[k]
            while i < N:
                if self.FREQ.get(frag, 0) > 0:
                    tmplist.append(i)
                i += 1
                frag = sentence[k:i + 1]
            if not tmplist:
                tmplist.append(k)
            DAG[k] = tmplist
        return DAG

    def get_dict_file(self):
        if self.dictionary == DEFAULT_DICT:
            return get_module_res(DEFAULT_DICT)
        else:
            return open(self.dictionary, 'rb')

    def calc(self, sentence, DAG, route):
        N = len(sentence)
        route[N] = (0, 0)

        logtotal = math.log(self.total)
        for idx in range(N - 1, -1, -1):  # 逆序规划 选择一条整个路径频率最大的句子
            route[idx] = max((math.log(self.FREQ.get(sentence[idx:x + 1]) or 1) -
                              logtotal + route[x + 1][0],
                              x) for x in DAG[idx])  # x 终点索引点 idx 考察开始点

    def __cut_DAG(self, sentence, new_word_find=None):

        if new_word_find is None:
            new_word_find = default_new_word_find

        DAG = self.get_DAG(sentence)
        route = {}
        self.calc(sentence, DAG, route)

        x = 0
        buf = ''
        N = len(sentence)
        while x < N:
            y = route[x][1] + 1
            l_word = sentence[x:y]
            if y - x == 1:
                buf += l_word  # 单字母或单字
            else:
                if buf:
                    yield buf
                    buf = ''
                    # if len(buf) == 1:  # 夹着的单字
                    #     yield buf
                    #     buf = ''
                    # else:
                    #     yield buf
                    #     if not self.FREQ.get(buf):  # 词典里找不到的词 用HMM来分
                    #         recognized = new_word_find(buf)
                    #         for t in recognized:
                    #             yield t
                    #     else:
                    #         for elem in buf:
                    #             yield elem
                    #     buf = ''

                yield l_word  # 找到的词优先输出
            x = y

        # 纯单字母或单字的情况
        if buf:
            yield buf
            # if len(buf) == 1:
            #     yield buf
            # elif not self.FREQ.get(buf):
            #     recognized = hmm_cut(buf)
            #     for t in recognized:
            #         yield t
            # else:
            #     for elem in buf:
            #         yield elem

    def seg(self, sentence):
        """
        同 cut 返回列表
        :param sentence:
        :return:
        """
        return list(self.cut(sentence))

    def cut(self, sentence):

        """
        The main function that segments an entire sentence that contains
        Chinese characters into seperated words.

        Parameter:
            - sentence: The str(unicode) to be segmented.
            - HMM: Whether to use the Hidden Markov Model.
        """
        sentence = strdecode(sentence)

        re_skip = re_skip_default
        cut_block = self.__cut_DAG
        re_han = re_han_default

        blocks = re_han.split(sentence)

        for blk in blocks:

            if not blk:  # 空白符号跳过

                continue
            if re_han.match(blk):  # 中文符号 核心分词在这里
                for word in cut_block(blk):
                    yield word
            else:
                tmp = re_skip.split(blk)
                for x in tmp:
                    if re_skip.match(x):  # 多个空白不分开
                        yield x
                    else:
                        yield x
                        # for xx in x:  # 剩下来的全部分开
                        #     yield xx

    def load_userdict(self, f):
        '''
        Load personalized dict to improve detect rate.
        Parameter:
            - f : A plain text file contains words and their ocurrences.
                  Can be a file-like object, or the path of the dictionary file,
                  whose encoding must be utf-8.
        Structure of dict file:
        word1 freq1 word_type1
        word2 freq2 word_type2
        ...
        Word type may be ignored
        '''
        self.check_initialized()
        if isinstance(f, str):
            f_name = f
            f = open(f, 'rb')
        else:
            f_name = resolve_filename(f)
        for lineno, ln in enumerate(f, 1):
            line = ln.strip()
            if not isinstance(line, str):
                try:
                    line = line.decode('utf-8').lstrip('\ufeff')
                except UnicodeDecodeError:
                    raise ValueError('dictionary file %s must be utf-8' % f_name)
            if not line:
                continue
            # match won't be None because there's at least one character
            word, freq, tag = re_userdict.match(line).groups()
            if freq is not None:
                freq = freq.strip()
            if tag is not None:
                tag = tag.strip()
            self.add_word(word, freq, tag)

    def add_word(self, word, freq=None, tag=None):
        """
        Add a word to dictionary.
        freq and tag can be omitted, freq defaults to be a calculated value
        that ensures the word can be cut out.
        """
        self.check_initialized()
        word = strdecode(word)
        freq = int(freq) if freq is not None else self.suggest_freq(word, False)
        self.FREQ[word] = freq
        self.total += freq
        if tag:
            self.user_word_tag_tab[word] = tag
        for ch in range(len(word)):
            wfrag = word[:ch + 1]
            if wfrag not in self.FREQ:
                self.FREQ[wfrag] = 0
        # if freq == 0:
        #    finalseg.add_force_split(word)

    def suggest_freq(self, segment, tune=False):
        """
        Suggest word frequency to force the characters in a word to be
        joined or splitted.
        Parameter:
            - segment : The segments that the word is expected to be cut into,
                        If the word should be treated as a whole, use a str.
            - tune : If True, tune the word frequency.
        Note that HMM may affect the final result. If the result doesn't change,
        set HMM=False.
        """
        self.check_initialized()
        ftotal = float(self.total)
        freq = 1
        if isinstance(segment, str):
            word = segment
            for seg in self.cut(word):
                freq *= self.FREQ.get(seg, 1) / ftotal
            freq = max(int(freq * self.total) + 1, self.FREQ.get(word, 1))
        else:
            segment = tuple(map(strdecode, segment))
            word = ''.join(segment)
            for seg in segment:
                freq *= self.FREQ.get(seg, 1) / ftotal
            freq = min(int(freq * self.total), self.FREQ.get(word, 0))
        if tune:
            self.add_word(word, freq)
        return freq
