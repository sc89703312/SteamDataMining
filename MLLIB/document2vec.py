from pyspark.ml.feature import Word2Vec
from pyspark import SparkContext, SQLContext, SparkConf
from pyspark.sql import Row

sc = SparkContext("local[*]")
sqlContext = SQLContext(sc)

row = Row("text")
def process_line(line):
    tokens = line.strip().split(" ")
    res = []
    for item in tokens:
        res.append(item.split("/")[0])
    return res

# Input data: Each row is a bag of words from a sentence or document.
documentDF = sc.textFile("data/sg.txt").map(process_line).map(row).toDF()
documentDF.printSchema()
print(documentDF.head())

# Learn a mapping from words to Vectors.
word2Vec = Word2Vec(vectorSize=200, minCount=0, inputCol="text", outputCol="result")
model = word2Vec.fit(documentDF)

fw = open("data/features_word2vec.txt", "w", encoding='utf-8')

result = model.transform(documentDF)
for row in result.collect():
    text, vector = row

    fw.write(" ".join([str(i) for i in vector]))
    fw.write("\n")