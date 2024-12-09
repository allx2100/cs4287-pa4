from pyspark import SparkConf, SparkContext
from pyspark.sql import SparkSession

MONGO_DB_IP = "mongodb://10.83.154.205"
MONGO_DB_PORT = "27017"
mongo_db_host = f"{MONGO_DB_IP}:{MONGO_DB_PORT}"

conf = SparkConf()
conf.set("spark.jars.packages",
             "org.mongodb.spark:mongo-spark-connector_2.12:10.4.0")

conf.set("spark.mongodb.read.connection.uri", mongo_db_host)
conf.set("spark.mongodb.read.database", "kafka_db")
conf.set("spark.mongodb.read.collection", "images")

conf.set("spark.mongodb.write.connection.uri", mongo_db_host)
conf.set("spark.mongodb.write.database", "kafka_db")
conf.set("spark.mongodb.write.collection", "images")
conf.set("spark.mongodb.write.operationType", "update")

SparkContext(conf=conf)

spark = SparkSession.builder \
    .appName("Manual-MapReduce-Accuracy") \
    .getOrCreate()

print('connected to collection')

images_df = spark.read.format("mongodb").load()

images_rdd = images_df.rdd

mapped_rdd = images_rdd.map(lambda row: (
    row['producer_num'],
    (1 if row['prediction'] == row['label'] else 0, 1)
))

reduced_rdd = mapped_rdd.reduceByKey(lambda a, b: (
    a[0] + b[0], 
    a[1] + b[1]
))

accuracy_rdd = reduced_rdd.map(lambda x: (
    x[0],  
    x[1][0], 
    x[1][1], 
    x[1][0] / x[1][1] 
))

accuracy_df = accuracy_rdd.toDF(["producer_num", "correct_predictions", "total_predictions", "accuracy"])

accuracy_df.show()
