import os
import numpy as np
from gensim.models import *

# file_path = os.path.join("/Users/echo/Desktop/SK_Learning/NaturalLanguageProcess/WordSegment/Tencent_AILab_ChineseEmbedding",
#                          "Tencent_AILab_ChineseEmbedding.txt")

file_path = os.path.join("/Users/echo/Desktop/SK_Learning/WordEmbedding/data", "zho.model2.bin")
model = KeyedVectors.load_word2vec_format(file_path, binary=True)
# print(type(model.vocab))
vocab_dict = model.vocab
print(type(vocab_dict))
print(model['我'].shape)

fo = open("data/sg.txt", 'r', encoding='utf-8')
fw = open("data/features_tencent2vec.txt", 'w', encoding='utf-8')
comments = fo.readlines()
for comment in comments:
    res = np.zeros(200)
    counter = 0
    tokens = comment.split(" ")
    for token in tokens:
        token = token.split("/")[0]
        if token in vocab_dict:
            res += model[token]
            counter += 1
        else:
            for character in token:
                if character in vocab_dict:
                    res += model[character]
                    counter += 1
    if not counter == 0:
        res /= counter

    fw.write(" ".join([str(i) for i in res]))
    fw.write("\n")


