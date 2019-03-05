#!/usr/bin/env python
# -*-coding:utf-8-*-

import re

re_userdict = re.compile('^(.+?)( [0-9]+)?( [a-z]+)?$')
re_eng = re.compile('[a-zA-Z0-9]')

re_han_default = re.compile(r"([\u4E00-\u9FD5a-zA-Z0-9+#&\._%\-]+)")
re_skip_default = re.compile(r"([\r\n|\s]+)")

DEFAULT_DICT = 'dict.txt'

CATERING_DICT = 'catering_dict.txt'

DEFALUT_CACHE_NAME = 'segment.cache'
