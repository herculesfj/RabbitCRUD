import json
import pika
from config import RABBITMQ_HOST, REQUEST_QUEUE
from repositories.user_repository import UserRepository
from monitoring.monitor_publisher import MonitorPublisher
from bson.objectid import ObjectId

class MessageHandler:
    def __init__(self, rabbit_host=RABBITMQ_HOST):
        self.repo = UserRepository()
        self.monitor = MonitorPublisher()
        params = pika.ConnectionParameters(host=rabbit_host)
        self.connection = pika.BlockingConnection(params)
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue=REQUEST_QUEUE, durable=True)

    def start(self):
        self.channel.basic_qos(prefetch_count=1)
        self.channel.basic_consume(queue=REQUEST_QUEUE, on_message_callback=self._on_message)
        print("[worker] Waiting for messages...")
        self.channel.start_consuming()

    def _on_message(self, ch, method, properties, body):
        try:
            message = json.loads(body)
            action = message.get("action")
            data = message.get("data", {})
            # process
            if action == "create":
                # data contains id and rest
                self.repo.insert(data)
                self.monitor.publish_event("create", "success")
            elif action == "update":
                # expecting name or id - adapt according to api
                # here assume data contains 'name' or 'id'
                if "id" in data:
                    _id = data["id"]
                    # remove id from update to avoid overwriting object id field
                    updated = {k: v for k, v in data.items() if k != "id"}
                    self.repo.update_by_id(_id, updated)
                self.monitor.publish_event("update", "success")
            elif action == "delete":
                if "id" in data:
                    self.repo.delete_by_id(data["id"])
                self.monitor.publish_event("delete", "success")
            else:
                self.monitor.publish_event(action or "unknown", "error", "Unknown action")
        except Exception as e:
            # publish error monitor event
            self.monitor.publish_event("processing", "error", str(e))
        finally:
            ch.basic_ack(delivery_tag=method.delivery_tag)
