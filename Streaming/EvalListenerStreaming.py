from pyspark import SparkContext
from pyspark.streaming import StreamingContext
import pprint
import random
import time
import os

from pyspark import SparkContext
from pyspark.streaming import StreamingContext

from SteamDataMining.DataRepresentation.StreamingDR import *
from flask_sse import sse

def eval_split(line):
    res = []
    for item in line.split(" "):
        res.append(int(item))
    return res

filepath = os.path.join(os.getcwd(), "eval_output", "eval_count_" + str(time.time()) + r".txt")

# Create a local StreamingContext with two working thread and batch interval of 1 second
sc = SparkContext("local[2]","EvalCounter")
ssc = StreamingContext(sc, 1)

# 添加需要监听的本地路径
# lines = ssc.textFileStream("file://" + os.path.join(os.getcwd(), "eval"))
lines = ssc.textFileStream("hdfs://localhost:8020/user/echosheng/eval/")

res = lines.map(eval_split).map(sum)

def processEachRDD(rdd):
    eval_counts = rdd.collect()
    len_eval_counts = len(eval_counts)

    if not len_eval_counts == 0:

        ups = []
        downs = []
        counter = 0
        for item in eval_counts:
            if counter%2 == 0:
                ups.append(item)
            else:
                downs.append(item)
            counter += 1
        up_sum = sum(ups)
        down_sum = sum(downs)

        res_str = " ".join([str(up_sum), str(down_sum)])
        fo = open(filepath, "a", encoding='utf-8')
        fo.write(res_str)
        fo.write("\n")
        fo.flush()
        fo.close()

        fr = open(filepath, "r", encoding='utf-8')
        lines = fr.readlines()
        ups = []
        downs = []
        evals = []

        up_ratio = []
        totals = []

        for line in lines:
            if not line == "":
                up_tmp, down_tmp = line.split(" ")
                up_tmp = int(up_tmp)
                down_tmp = int(down_tmp)
                eval_tmp = up_tmp + down_tmp

                ups.append(up_tmp)
                downs.append(down_tmp)
                evals.append(eval_tmp)

                up_ratio.append(100*sum(ups) / sum(evals))
                totals.append(sum(evals))


        print("totals: {}, ratio: {}".format(totals, up_ratio))

        with app.app_context():
            sse.publish({"totals": totals, "up_ratio": up_ratio, "max": totals[-1]}, type='eval')


res.foreachRDD(processEachRDD)

ssc.start()  # Start the computation
ssc.awaitTermination()  # Wait for the computation to terminate
