#!/usr/bin/env python
# -*-coding:utf-8-*-

import numpy

import spacy
from spacy.language import Language


def train_word_vectors(vectors_loc, lang='zh', model_name='zh_model'):
    """
    加载词向量数据 从零开始训练 spacy 模型
    :param vectors_loc:
    :param lang:
    :param model_name:
    :return:
    """
    if lang is None:
        nlp = Language()
    else:
        # create an empty language class
        nlp = spacy.blank(lang)
    with open(vectors_loc, 'rb') as file_:
        header = file_.readline()
        nr_row, nr_dim = header.split()
        print(nr_row, nr_dim)

        nlp.vocab.reset_vectors(width=int(nr_dim))

        count = 0
        for line in file_:
            line = line.rstrip().decode('utf8')
            pieces = line.rsplit(' ', int(nr_dim))
            word = pieces[0]
            vector = numpy.asarray([float(v) for v in pieces[1:]], dtype='f')
            # add the vectors to the vocab

            count += 1
            print(f'{word} added {count / int(nr_row) * 100} % ')

            nlp.vocab.set_vector(word, vector)
    nlp.to_disk("data/" + model_name)
    print('finishing!!!')
