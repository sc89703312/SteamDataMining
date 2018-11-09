import requests
from SteamDataMining.Weibo.url import *
import queue
import json
from pymongo import MongoClient

client = MongoClient('localhost', 27017)
collection = client.get_database("weibo").get_collection("follows")
profile_coll = client.get_database("weibo").get_collection("profile")

def datacrawl():
    start_id = 3579555650
    max_iteration = 0
    # max_iteration = 1
    # max_page_iteration = 20
    max_page_iteration = 50
    save_every = 50

    # fo = open("sava.json", "w", encoding='utf-8')


    users_to_do = queue.Queue()
    users_to_do.put(start_id)
    users_done = set()

    counter = 0
    while not users_to_do.empty() and counter <= max_iteration:
        cur_user_id = users_to_do.get()
        follows_ids = []
        for page_itr in range(1, max_page_iteration+1):
            url = FOLLOWS_LIST_URL.format(id=cur_user_id, page_num=page_itr)
            res = requests.get(url=url).json()
            if res['ok'] == 1 and res['data']['cards']:
                follows_group = res['data']['cards'][-1]['card_group']
                for follow in follows_group:
                    user_id = follow['user']['id']
                    follows_ids.append(user_id)
                    if user_id not in users_done:
                        users_to_do.put(user_id)

        counter += 1
        users_done.add(cur_user_id)
        print("User {}  follows : {}".format(cur_user_id, follows_ids))
        db_row = {"user_id": cur_user_id, "follows:": follows_ids}
        inserted_res = collection.insert_one(db_row)
        print("Counter {} inserted_id {}".format(counter, inserted_res.inserted_id))

        if counter%save_every == 0:
            print("User to do:{}".format(users_to_do))
            print("User done: {}".format(users_done))

def dataread():
    follows = collection.find()
    fo = open("relations.txt", "w", encoding='utf-8')
    for follow in follows:
        fan_id = follow['user_id']
        for follow_id in follow['follows:']:
            res_str = "{} {}".format(follow_id, fan_id)
            fo.write(res_str)
            fo.write("\n")
            fo.flush()
    fo.close()

def profileCrawl():
    follow_id_set = set()
    follows = collection.find()
    for item in follows:
        follow_id_set.add(item['user_id'])
        for follow in item['follows:']:
            follow_id_set.add(follow)



    print(len(follow_id_set))
    # print(follow_id_set)
    counter = 0
    for follow_id in follow_id_set:
        counter += 1
        if counter <= 15826:
            continue
        # print(follow_id)
        cur_url = PEOPLE_DETAIL_URL.format(id=follow_id)
        res = requests.get(cur_url)
        if res.status_code == 200:
            res = res.json()
            if res['ok'] == 1 and res['data']['userInfo']:
                userInfo = res['data']['userInfo']
                inserted_item = {
                    "id": userInfo['id'],
                    "screen_name": userInfo['screen_name'],
                    "description": userInfo['description'],
                    "followers_count": userInfo['followers_count'],
                    "follow_count": userInfo['follow_count']
                }
                profile_coll.insert_one(inserted_item)
                print("Complete {}".format(counter))

datacrawl()