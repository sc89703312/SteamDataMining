import os
import json
from pymongo import MongoClient

client = MongoClient('localhost', 27017)
comment_coll = client.get_database("steam").get_collection("comments")

positive_path = "data/positive/"
negative_path = "data/negative/"

sentences = {}

def list_all_files(path, sen):
    dir_path = os.path.join(os.getcwd(), path)
    files = os.listdir(dir_path)
    print(files)
    for file in files:
        if not file == ".DS_Store":
            fo = open(os.path.join(dir_path, file), 'r')
            lines = fo.readlines()
            sentences = []
            for line in lines:
                if not line == '' or not line == "\n":
                    sentences.append(line.strip("\n"))
            print(" ".join(sentences))
            comment_coll.insert_one({
                "sentence": " ".join(sentences),
                "sentiment": sen
            })

def process_mongo_data():
    comments = comment_coll.find()
    fo = open('data/comments.txt', 'w', encoding='utf-8')
    for comment in comments:
        fo.write(comment['sentence'])
        fo.write("\n")
    fo.flush()
    fo.close()
    fo = open('data/comments.txt', 'r', encoding='utf-8')

    print(len(fo.readlines()))

def process_feature_file():
    feature_path = os.path.join(os.getcwd(), "..", "..", "bert/comment/features.jsonl")
    fo = open('data/features.txt', 'w', encoding='utf-8')
    feature_vectors = []
    print(feature_path)
    counter = 0
    with open(feature_path, 'r', encoding='utf-8') as load_f:
        lines = load_f.readlines()
        lines_num = len(lines)
        for line in lines:
            features = json.loads(line)['features']
            # feature_vectors.append(features[0]['layers'][0]['values'])
            vector = features[0]['layers'][0]['values']
            str_vector = [str(i) for i in vector]
            fo.write(" ".join(str_vector))
            if not counter == lines_num - 1:
                fo.write("\n")
            print("Complete {}th line".format(counter))
            counter += 1

def libsvm():
    items = []
    fo = open('data/features_word2vec.txt', 'r', encoding='utf-8')
    # fo = open('data/features.txt', 'r', encoding='utf-8')
    comments = comment_coll.find()
    features = fo.readlines()

    for comment, feature in zip(comments, features):
        items.append({
            "sentiment": comment['sentiment'],
            "sentence": comment['sentence'],
            "features": feature.split(" ")
        })

    # fw = open('data/libsvm_classification.txt', 'w', encoding='utf-8')
    fw = open('data/libsvm_word2vec_classification.txt', 'w', encoding='utf-8')
    for item in items:
        features = item['features']
        features_ls = [str(index+1) + ":" + str(num)  for index,num in enumerate(features)]
        features_str = " ".join(features_ls)
        fw.write(str(item['sentiment']) + " " + features_str)

libsvm()



