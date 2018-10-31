from pymongo import MongoClient
import time
import pyhdfs
# from hdfs import *

client = MongoClient('127.0.0.1', 27017)
db = client.steam

fs = pyhdfs.HdfsClient('127.0.0.1:50070')
print(fs.listdir('/'))

counter = 0
flush_every = 5
tags_tmp = []
langs_tmp = []

raw_data = db.raw_data.find()
for item in raw_data:
    counter += 1
    # print(counter)

    weight_init = 2.5
    weight_decay = 0.1
    weight_counter = 0

    for tag in item['tags']:
        tags_tmp.append((tag, weight_init-weight_counter*weight_decay))
        weight_counter += 1
    for lang in item['langs']:
        langs_tmp.append(lang)

    if flush_every == counter:
        filepath = 'data/tmp_' + str(time.time()) + r".txt"

        res_str = ""
        tag_counter = 0
        for tag_tmp in tags_tmp:
            res_str += (tag_tmp[0] + "," + str(tag_tmp[1]))
            if not tag_counter == len(tags_tmp) - 1:
                res_str += "/"
            tag_counter += 1

        fs.create('/user/echosheng/' + filepath, data=res_str)
        print("complete")
        tags_tmp = []
        langs_tmp = []
        counter = 0

        time.sleep(2)
