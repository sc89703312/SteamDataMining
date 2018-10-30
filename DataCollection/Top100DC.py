from pymongo import MongoClient
import json
import requests
import re

client = MongoClient('localhost', 27017)

def processTop100Games():
    filepath = "steam_games_top100.json"
    with open(filepath, 'r', encoding='utf-8') as top100file:
        top100dict = json.load(top100file)

    print(top100dict.values())
    print([top100dict])
    db = client.steam
    res = db.raw_data.insert_many(top100dict.values())
    print(res.inserted_ids)

    print(top100dict.keys())
    fo = open('top100_appids.txt', 'w', encoding='utf-8')
    fo.write(" ".join(top100dict.keys()))

def processTop100GamesTags():
    tags_filepath = "top100_tags.txt"
    appids_filepath = "top100_appids.txt"
    tags_file = open(tags_filepath, 'r', encoding='utf-8')
    appids_file = open(appids_filepath, 'r', encoding='utf-8')

    appids = appids_file.readline().split()
    tags = tags_file.readlines()


    for appid, tag in zip(appids, tags):
        query = {"appid": int(appid)}
        tag_split = tag.split(",")
        tag_split[-1] = tag_split[-1].split("\n")[0]

        # print(tag.split(","))
        values = {"$set": {"tags": tag_split}}
        db = client.steam
        res = db.raw_data.update_one(query, values)
        print(res.modified_count)

def processTop100GamesLangs():
    appids_filepath = "top100_appids.txt"
    languages_filepath = "top100_languages.txt"

    appids_file = open(appids_filepath, 'r', encoding='utf-8')
    fo = open(languages_filepath, 'a', encoding='utf-8')
    appids = appids_file.readline().split()
    appids_todo = []

    for appid in appids:
        params = {"l": "en", "appids" : int(appid), "filters": "basic"}
        url = "http://store.steampowered.com/api/appdetails/"
        res = requests.get(url=url, params=params)
        if res.json()[appid]['success']:
            langs = res.json()[appid]['data']['supported_languages']

            # print(langs)
            langs_split = langs.split(", ")
            langs_res = []
            for lang in langs_split:
                match = re.search('([0-9A-Za-z\-\s]*)(<br>)?<strong>\*</strong>', lang)
                if match:
                    langs_res.append(match.group(1))
                else:
                    langs_res.append(lang)
            fo.write(appid+":"+"/".join(langs_res))
            fo.write("\n")
            fo.flush()
        else:
            print(appid + " not completed")
            appids_todo.append(appid)

def processTop100LangsMongo():
    file_path = "top100_languages.txt"
    file = open(file_path, 'r', encoding='utf-8')
    langs = file.readlines()
    for line in langs:
        appid, langs = line.split(":")
        langs_split = langs.split("/")
        langs_split[-1] = langs_split[-1].split("\n")[0]

        query = {"appid": int(appid)}
        values = {"$set": {"langs": langs_split}}
        db = client.steam
        res = db.raw_data.update_one(query, values)
        print(res.modified_count)

processTop100LangsMongo()
