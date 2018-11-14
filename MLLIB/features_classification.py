from pyspark.ml.linalg import Vectors
from pyspark.ml.classification import LinearSVC, LinearSVCModel, LogisticRegression, LogisticRegressionModel,MultilayerPerceptronClassifier, MultilayerPerceptronClassificationModel
from pyspark import SparkContext, SQLContext, SparkConf
from pyspark.ml.feature import Word2Vec
from pyspark.ml.evaluation import MulticlassClassificationEvaluator
from pyspark.sql import Row
from pyspark.sql.types import StructType, StructField, LongType, StringType
from pymongo import MongoClient

# 加载mongodb数据
client = MongoClient('localhost', 27017)
comment_coll = client.get_database("steam").get_collection("comments")
comment_list = comment_coll.find()
comments = []
for comment in comment_list:
    comments.append(comment)

# 计算特征向量的维数
# feature_file_path = "/Users/echo/Desktop/SK_Learning/SteamDataMining/MLLIB/data/libsvm_classification.txt"
# feature_file_path = "/Users/echo/Desktop/SK_Learning/SteamDataMining/MLLIB/data/libsvm_word2vec_classification.txt"
feature_file_path = "/Users/echo/Desktop/SK_Learning/SteamDataMining/MLLIB/data/libsvm_tencent2vec_classification.txt"

with open(feature_file_path, 'r', encoding='utf-8') as fo:
    head = fo.readline()
    feature_size = len(head.split(" "))-1

sc = SparkContext("local[*]")
sqlContext = SQLContext(sc)

# 处理libsvm格式的特征向量数据
inputData = sqlContext.read.format("libsvm").load(feature_file_path)
row_with_index = Row("label", "features", "comment")
schema  = StructType(
    inputData.schema.fields[:] + [StructField("comment", StringType(), False)])
indexed = (inputData.rdd # Extract rdd
    .zipWithIndex() # Add index
    .map(lambda ri: row_with_index(*list(ri[0]) + [comments[ri[1]]['sentence']])) # Map to rows
    .toDF(schema)) # It will work without schema but will be more expensive

# 切分数据，90%为训练数据，10%为测试数据
(train, test) = indexed.randomSplit([0.9, 0.1])

def Logistic():
    # Create a LogisticRegression instance. This instance is an Estimator.
    lr = LogisticRegression(maxIter=10, regParam=0.01)
    # Print out the parameters, documentation, and any default values.
    print("LogisticRegression parameters:\n" + lr.explainParams() + "\n")

    # Learn a LogisticRegression model. This uses the parameters stored in lr.
    lrModel = lr.fit(train)
    lrModel.write().overwrite().save("save/bert_logistic")

    # Make predictions on test data using the Transformer.transform() method.
    # LogisticRegression.transform will only use the 'features' column.
    # Note that model2.transform() outputs a "myProbability" column instead of the usual
    # 'probability' column since we renamed the lr.probabilityCol parameter previously.
    predictions = lrModel.transform(test)
    evaluator = MulticlassClassificationEvaluator(
        labelCol="label", predictionCol="prediction", metricName="accuracy")
    accuracy = evaluator.evaluate(predictions)
    print("Test Accuracy = %g " % accuracy)

def SVM():
    lsvc = LinearSVC(maxIter=100, regParam=0.1)

    # Fit the model
    lsvcModel = lsvc.fit(train)
    lsvcModel.write().overwrite().save("save/bert_svc")

    # Print the coefficients and intercept for linear SVC
    print("Coefficients: " + str(lsvcModel.coefficients))
    print("Intercept: " + str(lsvcModel.intercept))

    # Select (prediction, true label) and compute test error
    predictions = lsvcModel.transform(test)
    predictions.select("prediction", "label", "features")
    evaluator = MulticlassClassificationEvaluator(
        labelCol="label", predictionCol="prediction", metricName="accuracy")
    accuracy = evaluator.evaluate(predictions)
    print("Test Accuracy = %g " % accuracy)

def FeedforwardNeuralNet(input_size):
    # specify layers for the neural network:
    # input layer of size 4 (features), two intermediate of size 5 and 4
    # and output of size 3 (classes)
    layers = [input_size, 100, 20, 2]

    # create the trainer and set its parameters
    trainer = MultilayerPerceptronClassifier(maxIter=100, layers=layers, blockSize=128, seed=1234)

    # train the model
    model = trainer.fit(train)
    model.write().overwrite().save("save/tencent2vec_nn")

    # compute accuracy on the test set
    result = model.transform(test)
    # result.select("prediction", "label").show(400)
    predictionAndLabels = result.select("prediction", "label")
    evaluator = MulticlassClassificationEvaluator(metricName="accuracy")
    print("Test set accuracy = " + str(evaluator.evaluate(predictionAndLabels)))

def test_model():
    # model = LinearSVCModel.load("save/bert_svc")
    # model = LogisticRegressionModel.load("save/bert_logistic")
    # model = MultilayerPerceptronClassificationModel.load("save/word2vec_nn")
    model = MultilayerPerceptronClassificationModel.load("save/tencent2vec_nn")

    predictions = model.transform(test)

    # Select (prediction, true label) and compute test error
    evaluator = MulticlassClassificationEvaluator(
        labelCol="label", predictionCol="prediction", metricName="accuracy")
    accuracy = evaluator.evaluate(predictions)
    print("Test Accuracy = %g " % accuracy)

    result = predictions.select("prediction", "label", "comment").collect()
    for row in result:
        print("label=%s, prediction=%s, comment=%s"
              % (row.label, row.prediction, row.comment))

# FeedforwardNeuralNet(feature_size)
# test_model()