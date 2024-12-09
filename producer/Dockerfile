FROM bitnami/kafka:latest

USER root

RUN apt-get update && \
    apt-get install -y python3 python3-venv && \
    apt-get clean

WORKDIR /app

RUN python3 -m venv /app/venv

COPY requirements.txt .
RUN /app/venv/bin/pip install --no-cache-dir -r requirements.txt

COPY data.pkl .
COPY start_producer.sh .
COPY producer.py .
COPY sample_image.py .
COPY utils.py .

EXPOSE 2181 9092

ENV PATH="/app/venv/bin:$PATH"

CMD ["bash", "start_producer.sh"]