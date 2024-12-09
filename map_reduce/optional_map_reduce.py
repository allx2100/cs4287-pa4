from pyspark.sql import SparkSession
from pyspark.sql.functions import col, from_json, regexp_extract, expr
from pyspark.sql.types import StructType, StringType
import time

kafka_broker = "10.83.79.107:9092"
kafka_topic_regex = "inference_result_.*"

message_schema = StructType() \
    .add("label", StringType()) \
    .add("prediction", StringType())

spark = SparkSession.builder \
    .appName("Structured-Streaming-Aggregation") \
    .config("spark.sql.streaming.forceDeleteTempCheckpointLocation", "true") \
    .getOrCreate()

kafka_stream = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", kafka_broker) \
    .option("subscribePattern", kafka_topic_regex) \
    .option("startingOffsets", "latest") \
    .load()

messages_with_producer = kafka_stream.withColumn(
    "producer_num", regexp_extract(col("topic"), r"inference_result_(\d+)", 1)
)

parsed_messages = messages_with_producer.selectExpr("CAST(value AS STRING) as message", "producer_num") \
    .select(from_json(col("message"), message_schema).alias("data"), "producer_num") \
    .select("producer_num", "data.label", "data.prediction")

mapped_df = parsed_messages.withColumn("is_correct", expr("CASE WHEN label = prediction THEN 1 ELSE 0 END"))

batch_data = mapped_df.writeStream \
    .outputMode("append") \
    .format("memory") \
    .queryName("batch_data") \
    .trigger(processingTime="1 second") \
    .start()

time.sleep(15) # change for however long you want to run this
batch_data.stop()

final_df = spark.sql("""
    SELECT 
        producer_num, 
        SUM(is_correct) as correct_predictions, 
        COUNT(*) as total_predictions, 
        SUM(is_correct) * 1.0 / COUNT(*) as accuracy 
    FROM batch_data 
    GROUP BY producer_num
""")

print("Final aggregated metrics across all batches:")
final_df.show()