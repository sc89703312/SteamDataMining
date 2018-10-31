from pymongo import MongoClient
import time
import pyhdfs

client = MongoClient('localhost', 27017)
db = client.steam

fs = pyhdfs.HdfsClient('127.0.0.1:50070')
print(fs.listdir('/'))

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
            filepath = 'eval/tmp_' + str(time.time()) + r".txt"
            res_str = " ".join(ups) + "\n" + " ".join(downs)

            fs.create('/user/echosheng/' + filepath, data=res_str)

            ups = []
            downs = []
            dates = []

            time.sleep(1)




    print(len(evaluations))

evalApp(10)



