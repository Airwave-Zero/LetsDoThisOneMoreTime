FROM python:3.10-slim

WORKDIR /app
COPY kafka_producer.py .
RUN pip install kafka-python
CMD ["python", "kafka_producer.py"]

FROM bitnami/spark:latest

# Install Python deps
RUN apt-get update && apt-get install -y python3 python3-pip
COPY requirements.txt .
RUN pip3 install -r requirements.txt

# Copy scripts into container
COPY commoncrawl.py .
COPY clean_jobs_Stream.py .
COPY full_job_pipeline.py .

# Default command
CMD ["bash"]