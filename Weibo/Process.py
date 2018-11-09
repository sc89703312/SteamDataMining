import random
from pymongo import MongoClient
from SteamDataMining.DataRepresentation.StreamingDR import *
from flask_sse import sse

client = MongoClient('localhost', 27017)
collection = client.get_database("weibo").get_collection("follows")
profile_coll = client.get_database("weibo").get_collection("profile")

def randomRGB():
    char_ls = ['0', '1', '2', '3', '4', '5', '6',
               '7', '8', '9', 'a', 'b', 'c','d', 'e', 'f']
    res = "#"
    for i in range(6):
        res += random.choice(char_ls)
    return res

fo = open("/Users/echo/Desktop/vertices.txt")
vertices = fo.readlines()
fo = open("/Users/echo/Desktop/edges.txt")
edges = fo.readlines()
print(len(vertices))
print(len(edges))

vertice_list = []
for vertice in vertices:
    vertice_id, vertice_num = vertice.split(" ")
    cur_profile = profile_coll.find_one({"id": int(vertice_id)})
    vertice_dict = {
        "color": randomRGB(),
        "id": vertice_id,
        "label":  cur_profile['screen_name'],
        "size": float(vertice_num),
        "x": random.randrange(-150, 150),
        "y": random.randrange(-150, 150)
    }
    # print(vertice_dict)
    vertice_list.append(vertice_dict)

edge_list = []
for edge in edges:
    src_id, target_id = edge.strip('\n').split(" ")
    edge_dict = {
        "size": 1,
        "sourceID": src_id,
        "targetID": target_id
    }
    edge_list.append(edge_dict)


print(vertice_list)
print(edge_list)

with app.app_context():
    sse.publish({"edges": edge_list, "nodes": vertice_list}, type='relation')
