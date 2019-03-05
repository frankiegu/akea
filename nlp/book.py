#!/usr/bin/env python
# -*-coding:utf-8-*-


from nltk.book import *
from nltk.text import Text

from nlp.corpus import zh_novel

santi = Text(zh_novel.words('santi.txt'))
print("santi:", santi.name)

hongloumeng = Text(zh_novel.words('hongloumeng.txt'))
print("hongloumeng:", hongloumeng.name)

doupocangqiong = Text(zh_novel.words('doupocangqiong.txt'))
print("doupocangqiong:", doupocangqiong.name)
