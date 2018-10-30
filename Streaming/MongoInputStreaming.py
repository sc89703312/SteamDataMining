from pymongo import MongoClient
import time

client = MongoClient('localhost', 27017)
db = client.steam


counter = 0
flush_every = 5
tags_tmp = []
langs_tmp = []

raw_data = db.raw_data.find()
for item in raw_data:
    counter += 1
    # print(counter)
    for tag in item['tags']:
        tags_tmp.append(tag)
    for lang in item['langs']:
        langs_tmp.append(lang)

    if flush_every == counter:
        fo = open('data/tmp_' + str(time.time()) + r".txt", "w", encoding='utf-8')
        fo.write("/".join(tags_tmp))
        fo.flush()
        fo.close()

        tags_tmp = []
        langs_tmp = []
        counter = 0

        time.sleep(2)
