import os

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "localhost")
QUEUE_NAME = "crud_queue"
