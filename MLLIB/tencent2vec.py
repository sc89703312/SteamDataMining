import os

file_path = os.path.join("/Users/echo/Desktop/SK_Learning/NaturalLanguageProcess/WordSegment/Tencent_AILab_ChineseEmbedding",
                         "Tencent_AILab_ChineseEmbedding.txt")

print(file_path)
fo = open(file_path, 'r', encoding='utf-8')
fo.readlines()
fo.close()