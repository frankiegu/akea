#!/usr/bin/env python
# -*-coding:utf-8-*-

import operator
import re
from nlp.utils import get_chinese_stopwords

re_han = re.compile(r"([\u4E00-\u9FD5a-zA-Z0-9+#&\._%\-]+)")


def is_number(s):
    try:
        float(s) if '.' in s else int(s)
        return True
    except ValueError:
        return False


def split_sentences(text):
    """
    Utility function to return a list of sentences.
    @param text The text that must be split in to sentences.
    """
    sentence_delimiters = re.compile(u'[.!?,;:，。！？；：\t\\\\"\\(\\)\\\'\u2019\u2013]|\\s\\-\\s')
    sentences = sentence_delimiters.split(text)
    return sentences

def separate_words(text, min_word_return_size):
    """
    Utility function to return a list of all words that are have a length greater than a specified number of characters.
    @param text The text that must be split in to words.
    @param min_word_return_size The minimum no of characters a word must have to be included.
    """
    splitter = re.compile('[^a-zA-Z0-9_\\+\\-/]')
    words = []
    for single_word in splitter.split(text):
        current_word = single_word.strip().lower()
        # leave numbers in phrase, but don't count as words, since they tend to invalidate scores of their phrases
        if len(current_word) > min_word_return_size and current_word != '' and not is_number(current_word):
            words.append(current_word)
    return words

def generate_candidate_keywords(sentences_list, stopwords_list):
    """
    将停用词去除

    :param sentence_list:
    :return:
    """
    sentences = []

    for sentence in sentences_list:
        for stopword in stopwords_list:
            sentence = sentence.replace(stopword, '|')

        sentences.append(sentence)

    phrase_list = []
    for sentence in sentences:
        phrases = sentence.split("|")
        for phrase in phrases:
            phrase = phrase.strip().lower()
            if phrase != "":
                phrase_list.append(phrase)

    return phrase_list


def calculate_word_scores(phraseList):
    word_frequency = {}
    word_degree = {}
    for phrase in phraseList:
        word_list = [phrase]
        word_list_length = len(word_list)
        word_list_degree = word_list_length - 1
        # if word_list_degree > 3: word_list_degree = 3 #exp.
        for word in word_list:
            word_frequency.setdefault(word, 0)
            word_frequency[word] += 1
            word_degree.setdefault(word, 0)
            word_degree[word] += word_list_degree  # orig.
            # word_degree[word] += 1/(word_list_length*1.0) #exp.
    for item in word_frequency:
        word_degree[item] = word_degree[item] + word_frequency[item]

    # Calculate Word scores = deg(w)/frew(w)
    word_score = {}
    for item in word_frequency:
        word_score.setdefault(item, 0)
        word_score[item] = word_degree[item] / (word_frequency[item] * 1.0)  # orig.
    # word_score[item] = word_frequency[item]/(word_degree[item] * 1.0) #exp.
    return word_score


def generate_candidate_keyword_scores(phrase_list, word_score):
    keyword_candidates = {}
    for phrase in phrase_list:
        keyword_candidates.setdefault(phrase, 0)
        word_list = [phrase]
        candidate_score = 0
        for word in word_list:
            candidate_score += word_score[word]
        keyword_candidates[phrase] = candidate_score
    return keyword_candidates


class CRake(object):
    """
    单文章的关键词自动提取 C-Chinese
    """

    def __init__(self, stop_words_list=None):
        if stop_words_list is None:
            stop_words_list = get_chinese_stopwords()

        self.stop_words_list = stop_words_list

    def run(self, text):
        sentence_list = split_sentences(text)

        phrase_list = generate_candidate_keywords(sentence_list, self.stop_words_list)

        word_scores = calculate_word_scores(phrase_list)

        keyword_candidates = generate_candidate_keyword_scores(phrase_list, word_scores)

        sorted_keywords = sorted(keyword_candidates.items(), key=operator.itemgetter(1), reverse=True)
        return sorted_keywords


if __name__ == '__main__':
    text = "来广州出差，住在附近的康莱德酒店，晚上开完会就慕名而来，大概七点四十分的样子到的，人还有很多。刚入座，服务员就热情地让我点各种前菜，什么黄瓜，目前，凤爪啥的，我们都很不钟意，他们就臭着脸走了，后面的服务，不知道是不是因为我们没接受他们的推销，他们的服务总是有点不让人那么愉快。我们想点很多推荐的菜，什么烧味腊味之类的，结果被告知全没了，各种心塞，然后就情绪爆发地点了一些乱七八糟的东西。黄金煎饺，一共十五个，很小一个，味道很不错。还有个什么汤，我忘记了，广州普通话不是很能适应，但是味道很不错，里面有丝瓜海鲜什么的。一份豆腐煲，豆腐很嫩很入味，我吃了里面很多黄瓜。一份油麦菜，无功无过，最后几乎都剩下了。亮点是他们家的鱼生，我们三个人要了个4.8斤的，量非常大，有很多酱料，要自己调。服务员说了很多先后顺序，我们愣是没懂，觉得复杂，所以我索性让服务员帮我弄了，就是先在特定的玻璃盘子上倒上耗油，抹抹盘底，然后放入鱼生，然后放上姜丝，柠檬草，葱丝等各种配料，任君挑选，然后淋上酱汁，拌一拌，就能吃了，我吃了口一点没吃出鱼腥味，还不错，但也没别人推荐的那么传神。鱼生之外的耍鱼肉做成了砂锅，鱼肉很苏很入味，蛮好吃的，但不是我的菜。鹅肠，非常入味，推荐，而且吃很多也不会很撑，没负罪感。饮料叫了份蔓越莓玫瑰汁，一般般吧。没啥推荐不推荐的。甜品叫了姜汁撞奶？本来就超爱吃，姜汁味非常浓郁，奶很滑嫩，温温的特别棒，是我最喜欢吃的一样。如果不是明天早上还有会，真想去点都德也尝尝早茶，唉，忧桑。"

    rake = CRake()
    keywords = rake.run(text)
    print(keywords)
