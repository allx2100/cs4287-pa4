# Cloud Computing Project 4 - Structure and Architecture

## K8 Cluster Architecture

### K8 Master
- We used the master node Dr. Gohkale made for the assignment.
- The master contained 12 worker nodes

### 1. MongoDB Server
- **Database:** MongoDB hosted locally.
- **Database Name:** `kafka_db`
- **Collection Name:** `image`
- **Description:** 
  - This pod hosts a MongoDB database where the raw images and their metadata are stored.
  - This data originates from our Kafka producer.
  - The `image` collection stores data related to the images from the CIFAR-10 dataset, including the metadata provided by the Kafka producer.
  - This pod  hosts MongoDB strictly directly in the cluster. Details for this DB can be found in the video demo.

### 2. DB Consumer
- **Function:** 
  - This pod serves as a consumer that takes the image from the producer(s) and sends it to the database.
- **Process:** 
  - The data processed on this pod adds to the MongoDB `image` collection.
    
### 3. Kafka & IoT (Inference) Producer
- **Data Source:** CIFAR-10 dataset.
- **Kafka Role:** 
  - Acts as the producer for Kafka, sending messages containing images to the DB and ML consumers.
  - Acts as a consumer for Kafka, taking in the predictions from the ML model in a separate pod.
- **Flow:** 
  - The Kafka producer fetches images from the CIFAR-10 dataset and publishes them to a Kafka topic. These messages are consumed by the DB consumer and ML consumer for inference. The ML consumer sends back a prediction for the image, and the producer will also calculate the prediction latency.

### 4. Inference Consumer & ML Model
- **Model:** Resnet-18
- **Role:** 
  - This pod runs a pre-trained Resnet-18 model to make predictions on the images from the CIFAR-10 dataset.
  - It acts as the inference consumer by processing the image data sent from the Kafka producer(s).
  - It also acts as a producer, sending its prediction back to the producer.
- **Flow:** 
  - Images are ingested from the Kafka topic, and the Resnet-18 model makes predictions on these images. The inference results are sent to DB for storage in MongoDB and sent back to the producer.

## Helm
We used Helm to automatically manage the creation of kafka broker and zookeeper pods in our cluster. You can see the parameters we used in the helm folder, both on the command line and the custom values.yaml configuration file.

## Spark
We used Apache Spark to get a per-producer accuracy of ML model predictions using Map Reduce. Here, we read directly from the MongoDB database. Code can be found in the map_reduce folder.

## Optional Part 1
We extended our implementation of MapReduce to automatically read from the Kafka streams instead of waiting for all the data to enter the MongoDB database. Implementation can also be found in the map_reduce folder, and it is at the end of our demo.

## Technologies
- **MongoDB:** Primary database system for storing and retrieving image data.
- **Kafka:** Message broker for streaming image data across the cluster.
- **CIFAR-10 Dataset:** Dataset used for image classification tasks.
- **Ansible:** Technology used to automate the creation and set-up of VMs.
- **Resnet-18:** Deep learning model used for making image predictions.
- **Docker:** Framework used to containerize all processes across the cluster.
- **Kubernetes**: Framework used to orchestrate our cluster and its corresponding containers.
- **Helm**: Framework used to automatically deploy kafka broker and zookepper pods on our K8 cluster.
- **Apache Spark**: Framework used for MapReduce calculations.