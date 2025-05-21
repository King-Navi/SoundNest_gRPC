import aio_pika
import json
from dotenv import load_dotenv
import os
from config.connection_rabbitmq import get_rabbitmq_url

load_dotenv()

QUEUE_NAME = "notifications-queue"
RABBITMQ_URL = get_rabbitmq_url()

async def publish_notification(notification: dict):
    """
    Sends a notification message to the notifications-queue in RabbitMQ.
    
    Expected format:
    {
        "title": "string",
        "sender": "string",
        "user_id": int,
        "notification": "string",
        "relevance": "low" | "medium" | "high"
    }
    """
    required_fields = {"title", "sender", "user_id", "notification", "relevance"}
    missing = required_fields - notification.keys()
    if missing:
        raise ValueError(f"Missing required fields: {', '.join(missing)}")

    connection = await aio_pika.connect_robust(RABBITMQ_URL)
    channel = await connection.channel()
    await channel.declare_queue(QUEUE_NAME, durable=True)

    body = json.dumps(notification).encode()

    await channel.default_exchange.publish(
        aio_pika.Message(body=body, delivery_mode=aio_pika.DeliveryMode.PERSISTENT),
        routing_key=QUEUE_NAME
    )

    print(f"[Producer] Sent notification message to '{QUEUE_NAME}': {notification}")
