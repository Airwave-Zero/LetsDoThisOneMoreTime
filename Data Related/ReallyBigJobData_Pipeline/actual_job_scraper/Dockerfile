FROM python:3.10-slim

WORKDIR /app
COPY kafka_producer.py .
RUN pip install kafka-python
CMD ["python", "kafka_producer.py"]