import requests
import json
import pprint
from pymongo import MongoClient

client = MongoClient('localhost', 27017)
db = client.steam

appids_filepath = "top100_appids.txt"
appids_file = open(appids_filepath, 'r', encoding='utf-8')
appids = appids_file.readline().split()

print(appids)
print(len(appids))

# appids = ["570"]
counter = 0
for appid in appids:
    url = "https://store.steampowered.com/appreviewhistogram/" + appid
    params = {"l": "schinese"}
    res = requests.get(url, params).json()
    if res['success'] == 1:
        results = res['results']
        item_info = {"appid": int(appid)}
        for key, value in results.items():
            item_info[key] = value
        insert_res = db.raw_evaluation.insert_one(item_info)
        print("process {}, appid: {}, inserted_id: {}".format(counter, appid, insert_res.inserted_id))
        counter += 1




