from pyspark.sql import SparkSession
from pyspark import SparkConf, SparkContext

myconf = SparkConf()
myconf.setAppName("test").setMaster("local[*]")

# 指定连接器对应的spark-package
myconf.set("spark.jars.packages", "org.mongodb.spark:mongo-spark-connector_2.11:2.3.1")
# 指定mongo地址，需要每个工作节点都能访问到
myconf.set("spark.mongodb.input.uri", "mongodb://127.0.0.1:27017/")
# 设置要读取的dbs名和collection名
myconf.set("spark.mongodb.input.database", "steam")
myconf.set("spark.mongodb.input.collection", "raw_data")
# 指定分区方式
# myconf.set("spark.mongodb.input.partitioner", "MongoSplitVectorPartitioner")

spark = SparkSession.builder.config(conf=myconf).getOrCreate()
# 使用指定格式读取
mg_data = spark.read.format("com.mongodb.spark.sql").load()
mg_data.printSchema()

# spark.stop()