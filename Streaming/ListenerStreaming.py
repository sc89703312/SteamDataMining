from pyspark import SparkContext
from pyspark.streaming import StreamingContext
import pprint
import random
import time
import os
from SteamDataMining.DataRepresentation.StreamingDR import *
from flask_sse import sse

# ------------------------------word count-----------------------------------------------------------
from pyspark import SparkContext
from pyspark.streaming import StreamingContext

filepath = os.path.join(os.getcwd(), "output", "tag_count_" + str(time.time()) + r".txt")
fo = open(filepath, "a", encoding='utf-8')

# Create a local StreamingContext with two working thread and batch interval of 1 second
sc = SparkContext("local[2]","TagsLangsCounter")
ssc = StreamingContext(sc, 4)

# 添加需要监听的本地路径
lines = ssc.textFileStream("file://" + os.path.join(os.getcwd(), "data"))

# Split each line into words
words = lines.flatMap(lambda line: line.split("/"))

# Count each word in each batch
pairs = words.map(lambda word: (word.split(",")[0], float(word.split(",")[1])))
wordCounts = pairs.reduceByKey(lambda x, y: x + y)

## 收集数据
def processEachRDD(rdd):
    tagCounts = rdd.collect()
    len_tag_counts = len(tagCounts)
    if not len_tag_counts == 0:
        ## 处理当前batch的tags 并写入到文件
        res_str = ""
        counter = 0
        for tagCount in tagCounts:
            res_str += (tagCount[0] + "," + str(tagCount[1]))
            if not counter == len_tag_counts-1:
                res_str += "/"
            counter += 1
        fo.write(res_str)
        fo.write("\n")
        fo.flush()

        ## 处理之前所有batch的tags 并输出到console
        cur_lines = sc.textFile("file://" + filepath)
        cur_tag_counts = cur_lines.flatMap(lambda line: line.split("/"))\
            .map(lambda count: (count.split(",")[0], float(count.split(",")[1])))\
            .reduceByKey(lambda x, y: x + y)\
            .sortBy(lambda x: x[1], ascending=False)\
            .collect()

        print(cur_tag_counts)

        ## 服务端主动推送 更新flask ui的图表数据
        with app.app_context():
            tags = []
            selected = {}
            entities = []
            counter = 0

            for item in cur_tag_counts:
                tags.append({"value": item[1], "name": item[0]})
                entities.append(item[0])
                if counter <= 10:
                    selected[item[0]] = True
                else:
                    selected[item[0]] = False

                counter += 1


            sse.publish({"tags": tags, "tag_entities": entities, "selected": selected}, type='greeting')


wordCounts.foreachRDD(processEachRDD)


ssc.start()  # Start the computation
ssc.awaitTermination()  # Wait for the computation to terminate