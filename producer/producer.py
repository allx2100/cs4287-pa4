import os
import time
import json
import threading
from kafka import KafkaProducer, KafkaConsumer
from sample_image import load_data, sample_image
import subprocess
import random

PRODUCER_NUM = random.randint(0, 100)

KAFKA_IMAGES_TOPIC = 'images'

def consume_inference_results(topic, original_message_ids, latency_results, producer_done):
    consumer = KafkaConsumer(bootstrap_servers='kafka.team12.svc.cluster.local:9092')
    consumer.subscribe(topics=[f"inference_result_{PRODUCER_NUM}"])

    while True:
        if producer_done.is_set() and not original_message_ids:
            break
            
        message = consumer.poll(timeout_ms=1000)
        
        if message:
            for _, messages in message.items():
                for msg in messages:
                    result = json.loads(msg.value.decode('utf-8'))
                    
                    original_message_id = result.get('id')
                    prediction = result.get('prediction')
                    start_time = result.get('start_time')
                    end_time = result.get('end_time')
        
                    if original_message_id in original_message_ids:
                        end_time = time.time()
                        response_time = round(end_time - result.get('start_time', 0), 5)
                        latency_results.append(response_time)
                        original_message_ids.remove(original_message_id)

    consumer.close()

def produce_messages(original_message_ids, producer_done):    
    producer = KafkaProducer(
        bootstrap_servers='kafka-broker-0.kafka-broker-headless.team12.svc.cluster.local:9092',
        acks=1
    )

    images, labels, filenames, label_names = load_data('data.pkl')

    for i in range(5000):
        index, image, label, filename = sample_image(images, labels, filenames)

        message = {
            "id": index,
            "label": label,
            "label_name": label_names[label].decode('utf-8'),
            "data": image.tolist(),
            "filename": filename,
            "start_time": time.time(),
            "producer_num": PRODUCER_NUM
        }

        message_bytes = json.dumps(message).encode('utf-8')

        
        producer.send(KAFKA_IMAGES_TOPIC, value=message_bytes)
        producer.flush()

        original_message_ids.append(message["id"])


    producer.close()

    producer_done.set()

if __name__ == "__main__":
    original_message_ids = []
    latency_results = []
    producer_done = threading.Event()

    consumer_thread = threading.Thread(
        target=consume_inference_results,
        args=('inference_result_' + str(PRODUCER_NUM), original_message_ids, latency_results, producer_done)
    )
    consumer_thread.start()

    produce_messages(original_message_ids, producer_done)

    consumer_thread.join()

    time.sleep(10)

    with open('latency_' + str(PRODUCER_NUM) + '.json', 'w') as json_file:
        json.dump(latency_results, json_file, indent=4)