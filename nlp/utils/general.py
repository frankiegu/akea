#!/usr/bin/env python
# -*-coding:utf-8-*-

import os
from mymodule.utils.path_utils import get_project_path


def get_chinese_stopwords():
    """
    获取中文停用词表
    :return:
    """
    stopwords_filename = os.path.join(get_project_path('dicts'), 'chinese_stopwords.txt')

    stopwords = []

    with open(stopwords_filename, 'rt', encoding='utf8') as f:
        for line in f:
            line = line.strip()
            stopwords.append(line)

    return stopwords
