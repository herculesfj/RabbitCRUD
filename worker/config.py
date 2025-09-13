import os
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "localhost")
REQUEST_QUEUE = "crud_queue"
MONITOR_QUEUE = "monitor_queue"
WORKER_ID = os.getenv("WORKER_ID", None)
