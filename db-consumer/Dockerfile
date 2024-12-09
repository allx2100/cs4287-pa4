FROM bitnami/kafka:latest

USER root

RUN apt-get update && \
    apt-get install -y python3 python3-venv && \
    apt-get clean

WORKDIR /app

RUN python3 -m venv /app/venv

COPY requirements.txt .
RUN /app/venv/bin/pip install --no-cache-dir -r requirements.txt

COPY consumer.py .
COPY start_consumer.sh .

RUN chmod +x start_consumer.sh

EXPOSE 27017 9092

ENV PATH="/app/venv/bin:$PATH"

CMD ["bash", "start_consumer.sh"]
