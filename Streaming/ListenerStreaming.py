from pyspark import SparkContext
from pyspark.streaming import StreamingContext
import pprint

# ------------------------------word count-----------------------------------------------------------
from pyspark import SparkContext
from pyspark.streaming import StreamingContext


fo = open("output/tag_count.txt", "a", encoding='utf-8')
# Create a local StreamingContext with two working thread and batch interval of 1 second
sc = SparkContext("local[2]","TagsLangsCounter")
ssc = StreamingContext(sc, 10)

# 添加需要监听的本地路径
lines = ssc.textFileStream("file:///Users/echo/Desktop/SK_Learning/SteamDataMining/Streaming/data/")

# Split each line into words
words = lines.flatMap(lambda line: line.split("/"))

# Count each word in each batch
pairs = words.map(lambda word: (word, 1))
wordCounts = pairs.reduceByKey(lambda x, y: x + y)

def processEachRDD(rdd):
    tagCounts = rdd.collect()
    if not len(tagCounts) == 0:
        res_str = ""
        for tagCount in tagCounts:
            res_str += (tagCount[0] + "," + str(tagCount[1]))
            res_str += "/"
        fo.write(res_str)
        fo.write("\n")
        fo.flush()


wordCounts.foreachRDD(processEachRDD)


ssc.start()  # Start the computation
ssc.awaitTermination()  # Wait for the computation to terminate  # Wait for the computation to terminate