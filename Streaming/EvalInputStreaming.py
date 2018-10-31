from pymongo import MongoClient
import time

client = MongoClient('localhost', 27017)
db = client.steam

flush_every = 5

def evalApp(appid):
    res = db.raw_evaluation.find_one({"appid": appid})
    evaluations = res['rollups']
    counter = 0
    ups = []
    downs = []
    dates = []

    total_num = len(evaluations)
    for evaluation in evaluations:
        counter += 1
        ups.append(str(evaluation['recommendations_up']))
        downs.append(str(evaluation['recommendations_down']))
        dates.append(str(evaluation['date']))

        if counter%flush_every == 0 or counter == total_num:
            fo = open('eval/tmp_' + str(time.time()) + r'.txt', 'w', encoding='utf-8')

            fo.write(" ".join(ups))
            fo.write("\n")
            fo.write(" ".join(downs))
            # fo.write("\n")
            # fo.write(" ".join(dates))

            fo.flush()
            fo.close()

            time.sleep(1)

            ups = []
            downs = []
            dates = []


    print(len(evaluations))

evalApp(570)



