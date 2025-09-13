import pika, json
from config import RABBITMQ_HOST, MONITOR_QUEUE
from datetime import datetime
import os
import uuid

WORKER_ID = os.getenv("WORKER_ID") or str(uuid.uuid4())

class MonitorPublisher:
    def __init__(self, host=RABBITMQ_HOST, queue=MONITOR_QUEUE):
        self.host = host
        params = pika.ConnectionParameters(host=self.host)
        self.connection = pika.BlockingConnection(params)
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue=queue, durable=True)
        self.queue = queue

    def publish_event(self, action: str, status: str = "success", error: str = None):
        event = {
            "worker_id": WORKER_ID,
            "action": action,
            "status": status,
            "error": error,
            "timestamp": datetime.utcnow().isoformat()
        }
        self.channel.basic_publish(exchange='', routing_key=self.queue, body=json.dumps(event), properties=pika.BasicProperties(delivery_mode=2))

    def close(self):
        try:
            self.connection.close()
        except:
            pass
