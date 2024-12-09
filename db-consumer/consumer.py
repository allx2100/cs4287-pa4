import os
import time
import json
from kafka import KafkaConsumer
from pymongo import MongoClient

MONGO_DB_IP = os.getenv('DB_SERVICE_SERVICE_HOST', 'db-service')
MONGO_DB_PORT = os.getenv('DB_SERVICE_SERVICE_PORT', '27017')
mongo_db_host = MONGO_DB_IP + ":" + MONGO_DB_PORT
print(f"MongoDB host: {mongo_db_host}")

consumer = KafkaConsumer(bootstrap_servers='kafka.team12.svc.cluster.local:9092')
consumer.subscribe(topics=["images"])

client = MongoClient(f'mongodb://{mongo_db_host}/')
db = client['kafka_db']
collection = db['images']

for msg in consumer:
    try:
        message = json.loads(msg.value.decode('utf-8'))
        print(message)
        collection.insert_one(message)
    except json.JSONDecodeError:
        print("Received message is not a valid JSON")

consumer.close()
