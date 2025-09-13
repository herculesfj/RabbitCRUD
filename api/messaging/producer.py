import pika
import json
from config import RABBITMQ_HOST, QUEUE_NAME

class Producer:
    def __init__(self, host: str = RABBITMQ_HOST, queue: str = QUEUE_NAME):
        self.host = host
        self.queue = queue
        params = pika.ConnectionParameters(host=self.host)
        self.connection = pika.BlockingConnection(params)
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue=self.queue, durable=True)

    def publish(self, action: str, data: dict):
        message = {"action": action, "data": data}
        self.channel.basic_publish(
            exchange='',
            routing_key=self.queue,
            body=json.dumps(message),
            properties=pika.BasicProperties(delivery_mode=2)
        )

    def close(self):
        try:
            self.connection.close()
        except:
            pass
