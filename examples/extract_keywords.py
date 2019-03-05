#!/usr/bin/env python
# -*-coding:utf-8-*-


from sklearn.feature_extraction.text import TfidfVectorizer

n_features = 1000
n_top_words = 30


def print_top_words(model, feature_names, n_top_words):
    for array in model.toarray():
        words = [feature_names[i] for i in array.argsort()[:-n_top_words - 1:-1]]
        print(words)


print("Loading dataset...")
import os
from nlp.utils import get_data_path

data_path = get_data_path()
df_reviews_filename = os.path.join(data_path, 'df_reviews.pkl')
import pickle

with open(df_reviews_filename, 'rb') as f:
    df_reviews = pickle.load(f)
all_merchant = list(set(df_reviews['Merchant'].values))

contents = []
for merchant in all_merchant:
    df_one = df_reviews[df_reviews['Merchant'] == merchant]

    content_one = []
    for row in df_one.itertuples():

        content = row[3]
        if isinstance(content, str):
            content_one.append(content)
    contents.append(' '.join(content_one))
    print(f'{merchant} processed ok.')

from nlp.segment import Segment

import re


def is_number_word(s):
    """
    :return:
    """
    g = re.match(r'[\d]+', s)

    if g:
        return True
    return False


def remove_number_word(sl):
    return [s for s in sl if not is_number_word(s)]


seg = Segment()
X_contents = []
count = 0
for content in contents:
    if isinstance(content, str):
        res = seg.seg(content)
        # remove number word
        res = remove_number_word(res)

        space_res = ' '.join(res)
        X_contents.append(space_res)
        print(f'content segment finished. {count / len(all_merchant) * 100} %')
    else:
        print(content)
    count += 1
from nlp.utils import get_chinese_stopwords

chinese_stopwords = get_chinese_stopwords()

tf_vectorizer = TfidfVectorizer(max_df=0.95, min_df=2,
                                max_features=n_features,
                                stop_words=chinese_stopwords)

tf = tf_vectorizer.fit_transform(X_contents)

tf_feature_names = tf_vectorizer.get_feature_names()

print(f'feature_names: {tf_feature_names}')

print(f'all_merchants: {all_merchant}')

print_top_words(tf, tf_feature_names, n_top_words)
