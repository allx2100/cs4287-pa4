import os
import time
import json
from kafka import KafkaConsumer, KafkaProducer
from resnet import resnet18
import torch
from pymongo import MongoClient

MONGO_DB_IP = os.getenv('DB_SERVICE_SERVICE_HOST', 'db-service')
MONGO_DB_PORT = os.getenv('DB_SERVICE_SERVICE_PORT', '27017')
mongo_db_host = MONGO_DB_IP + ":" + MONGO_DB_PORT

consumer = KafkaConsumer(
    "images",
    bootstrap_servers="kafka.team12.svc.cluster.local:9092",
    value_deserializer=lambda x: json.loads(x.decode('utf-8'))
)

producer = KafkaProducer(
    bootstrap_servers=["kafka-broker-0.kafka-broker-headless.team12.svc.cluster.local:9092"],
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

model = resnet18(pretrained=True)

client = MongoClient(f'mongodb://{mongo_db_host}/')
db = client['kafka_db']
collection = db['images']

for msg in consumer:
    print('received')

    message = msg.value

    image_id = message['id']
    data = message['data']
    label = message['label']

    producer_num = message.get('producer_num')
    result_topic = f"inference_result_{producer_num}"

    data = torch.tensor(data).reshape((1, 3, 32, 32)).to(dtype=torch.float32)

    model.eval()

    with torch.no_grad():
        output = model(data)

    _, predicted_class = torch.max(output, 1)

    message['prediction'] = predicted_class.item()

    collection.update_one(
        {'id': image_id},
        {'$set': message},
        upsert=True
    )

    print(f"Label: {message['label']}, Prediction: {message['prediction']}", flush=True)

    inference_result = {
        'id': image_id,
        'prediction': predicted_class.item(),
        'label': label,
        'start_time': message.get('start_time', time.time()),
        'end_time': time.time()
    }

    producer.send(result_topic, value=inference_result)
    producer.flush()

    print(f'Inference result sent to Kafka topic: {result_topic}', flush=True)

consumer.close()
producer.close()