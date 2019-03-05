#!/usr/bin/env python
# -*-coding:utf-8-*-


"""

定义 S(A-B) = mean(S(A->B) + S(A<-B))

"""
import math


def calc_entropy(p):
    """
    计算信息熵
    :param p:
    :return:
    """
    entropy = - (p) * math.log(p, 2)
    return entropy


def calc_free_entropy():
    """

    计算自由熵 比如说A->B的自由熵 =

    :return:
    """
