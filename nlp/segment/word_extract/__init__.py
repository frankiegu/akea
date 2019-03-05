#!/usr/bin/env python
# -*-coding:utf-8-*-


"""

https://github.com/Moonshile/ChineseWordSegmentation
LICENSE MIT

"""

import re


def genSubparts(string):
    """
    Partition a string into all possible two parts, e.g.
    given "abcd", generate [("a", "bcd"), ("ab", "cd"), ("abc", "d")]
    For string of length 1, return empty list
    """
    length = len(string)
    res = []
    for i in range(1, length):
        res.append((string[0:i], string[i:]))
    return res


import math


def entropyOfList(ls):
    """
    Given a list of some items, compute entropy of the list
    The entropy is sum of -p[i]*log(p[i]) for every unique element i in the list, and p[i] is its frequency
    """
    elements = {}  # 计数 后面优化
    for e in ls:
        elements[e] = elements.get(e, 0) + 1
    length = float(len(ls))
    return sum([-v / length * math.log(v / length) for v in list(elements.values())])


def indexOfSortedSuffix(doc, max_word_len):
    """
    逐个取词

    Treat a suffix as an index where the suffix begins.
    Then sort these indexes by the suffixes.
    """
    indexes = []
    length = len(doc)
    for i in range(0, length):
        for j in range(i + 1, min(i + 1 + max_word_len, length + 1)):
            indexes.append((i, j))
    return sorted(indexes, key=lambda i_j: doc[i_j[0]:i_j[1]])


class WordInfo(object):
    """
    Store information of each word, including its freqency, left neighbors and right neighbors
    """

    def __init__(self, text):
        super(WordInfo, self).__init__()
        self.text = text
        self.freq = 0.0
        self.left = []
        self.right = []
        self.aggregation = 0

    def update(self, left, right):
        """
        Increase frequency of this word, then append left/right neighbors
        @param left a single character on the left side of this word
        @param right as left is, but on the right side
        """
        self.freq += 1
        if left: self.left.append(left)
        if right: self.right.append(right)

    def compute(self, length):
        """
        Compute frequency and entropy of this word
        @param length length of the document for training to get words
        """
        self.freq /= length
        self.left = entropyOfList(self.left)
        self.right = entropyOfList(self.right)

    def computeAggregation(self, words_dict):
        """
        Compute aggregation of this word
        @param words_dict frequency dict of all candidate words
        """
        parts = genSubparts(self.text)
        if len(parts) > 0:
            self.aggregation = min(
                [self.freq / words_dict[p1_p2[0]].freq / words_dict[p1_p2[1]].freq for p1_p2 in parts])


class WordExtracter():
    """
    根据信息熵来判断字与字之间的胶合度的一个词语抽取器

    """

    def __init__(self, doc, max_word_len=None, min_freq=0, min_entropy=0, min_aggregation=0):
        super(WordExtracter, self).__init__()

        if max_word_len is None:
            self.max_word_len = min(len(doc), 10)

        self.min_freq = min_freq
        self.min_entropy = min_entropy
        self.min_aggregation = min_aggregation

        self.word_infos = self.genWords(doc)

        # Result infomations, i.e., average data of all words
        word_count = float(len(self.word_infos))
        self.avg_len = sum([len(w.text) for w in self.word_infos]) / word_count
        self.avg_freq = sum([w.freq for w in self.word_infos]) / word_count
        self.avg_left_entropy = sum([w.left for w in self.word_infos]) / word_count
        self.avg_right_entropy = sum([w.right for w in self.word_infos]) / word_count
        self.avg_aggregation = sum([w.aggregation for w in self.word_infos]) / word_count
        # Filter out the results satisfy all the requirements

        filter_func = lambda v: len(
            v.text) > 1 and v.freq > self.min_freq and v.left > self.min_entropy and v.right > self.min_entropy

        self.word_with_freq = [(w.text, w.freq) for w in list(filter(filter_func, self.word_infos))]
        self.words = [w[0] for w in self.word_with_freq]

    def genWords(self, doc):
        """
        Generate all candidate words with their frequency/entropy/aggregation informations
        @param doc the document used for words generation
        """
        from nlp.utils.sentenses import split_sentenses
        #pattern = re.compile('[\\s\\d,.<>/?:;\'\"[\\]{}()\\|~!@#$%^&*\\-_=+a-zA-Z，。《》、？：；“”‘’｛｝【】（）…￥！—┄－]+')
        sentenses = split_sentenses(doc)
        word_cands = {}

        length = 0
        for sentense in sentenses:
            if re.match(r'[\s]+', sentense):  # 空白字符串 不用处理
                continue
            else:
                length += len(sentense)

            #sentense = re.sub(pattern, ' ', sentense)
            suffix_indexes = indexOfSortedSuffix(sentense, self.max_word_len)

            # compute frequency and neighbors
            for suf in suffix_indexes:
                word = sentense[suf[0]:suf[1]]
                if word not in word_cands:
                    word_cands[word] = WordInfo(word)
                word_cands[word].update(sentense[suf[0] - 1:suf[0]], sentense[suf[1]:suf[1] + 1])

        # compute probability and entropy
        for k in word_cands:
            word_cands[k].compute(length)

        # compute aggregation of words whose length > 1
        values = sorted(list(word_cands.values()), key=lambda x: len(x.text))
        for v in values:
            if len(v.text) == 1: continue
            v.computeAggregation(word_cands)
        return sorted(values, key=lambda v: v.freq, reverse=True)

    def segSentence(self, sentence):
        """
        Segment a sentence with the words generated from a document
        @param sentence the sentence to be handled
        @param method segmentation method
        """
        i = 0
        res = []
        while i < len(sentence):
            j_range = list(range(self.max_word_len, 0, -1))
            for j in j_range:
                if j == 1 or sentence[i:i + j] in self.words:
                    res.append(sentence[i:i + j])
                    i += j
                    break

        return res


if __name__ == '__main__':
    doc = '来广州出差，住在附近的康莱德酒店，晚上开完会就慕名而来，大概七点四十分的样子到的，人还有很多。刚入座，服务员就热情地让我点各种前菜，什么黄瓜，目前，凤爪啥的，我们都很不钟意，他们就臭着脸走了，后面的服务，不知道是不是因为我们没接受他们的推销，他们的服务总是有点不让人那么愉快。我们想点很多推荐的菜，什么烧味腊味之类的，结果被告知全没了，各种心塞，然后就情绪爆发地点了一些乱七八糟的东西。黄金煎饺，一共十五个，很小一个，味道很不错。还有个什么汤，我忘记了，广州普通话不是很能适应，但是味道很不错，里面有丝瓜海鲜什么的。一份豆腐煲，豆腐很嫩很入味，我吃了里面很多黄瓜。一份油麦菜，无功无过，最后几乎都剩下了。亮点是他们家的鱼生，我们三个人要了个4.8斤的，量非常大，有很多酱料，要自己调。服务员说了很多先后顺序，我们愣是没懂，觉得复杂，所以我索性让服务员帮我弄了，就是先在特定的玻璃盘子上倒上耗油，抹抹盘底，然后放入鱼生，然后放上姜丝，柠檬草，葱丝等各种配料，任君挑选，然后淋上酱汁，拌一拌，就能吃了，我吃了口一点没吃出鱼腥味，还不错，但也没别人推荐的那么传神。鱼生之外的耍鱼肉做成了砂锅，鱼肉很苏很入味，蛮好吃的，但不是我的菜。鹅肠，非常入味，推荐，而且吃很多也不会很撑，没负罪感。饮料叫了份蔓越莓玫瑰汁，一般般吧。没啥推荐不推荐的。甜品叫了姜汁撞奶？本来就超爱吃，姜汁味非常浓郁，奶很滑嫩，温温的特别棒，是我最喜欢吃的一样。如果不是明天早上还有会，真想去点都德也尝尝早茶，唉，忧桑。'

    # 领域优化



    ws = WordExtracter(doc, min_aggregation=0, min_entropy=0)
    print(' '.join(['%s:%f' % w for w in ws.word_with_freq]))
    print(' '.join(ws.words))
    print(' '.join(ws.segSentence(doc)))
    print('average len: ', ws.avg_len)
    print('average frequency: ', ws.avg_freq)
    print('average left entropy: ', ws.avg_left_entropy)
    print('average right entropy: ', ws.avg_right_entropy)
    print('average aggregation: ', ws.avg_aggregation)
