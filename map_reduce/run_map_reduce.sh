#!bin/bash

source team12venv/bin/activate

cd spark-3.5.3-bin-hadoop3

./bin/spark-submit \
    --master k8s://https://172.16.3.149:6443 \
    --deploy-mode client \
    --name spark-pi \
    --conf spark.executor.instances=3 \
    --conf spark.kubernetes.namespace=team12 \
    --conf spark.kubernetes.container.image=192.168.1.81:5000/common/spark-py \
    --packages org.mongodb.spark:mongo-spark-connector_2.12:10.4.0 \
    local:///home/cc/team12/cs4287-pa3/map_reduce.py