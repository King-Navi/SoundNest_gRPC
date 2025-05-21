import os
import json
import logging
from datetime import datetime
import aio_pika
import asyncio
from dotenv import load_dotenv
from pydantic import BaseModel, Field, ValidationError
from config.connection_rabbitmq import get_rabbitmq_url
from controller.utils.client_registry import ClientRegistry
from utils.wrappers.event_wrapper import EventResponse
from ..android_messaging import ClientAndroidNotifiacion


load_dotenv()

RABBITMQ_URL = get_rabbitmq_url()
COMMENT_REPLY_QUEUE = os.getenv("COMMENT_REPLY_QUEUE_NAME")

class CommentReplyPayload(BaseModel):
    messageContent: str = Field(..., description="Content of the comment reply")
    senderId: int       = Field(..., description="ID of the user sending the reply")
    senderName: str     = Field(..., description="Name of the user sending the reply")
    recipientId: int    = Field(..., description="ID of the user being replied to")
    recipientName: str  = Field(..., description="Name of the user being replied to")
    timestamp: datetime

async def start_consumer_comment_reply(
    client_registry: ClientRegistry,
    client_android_noti: ClientAndroidNotifiacion
):
    connection = await aio_pika.connect_robust(RABBITMQ_URL)
    channel = await connection.channel()
    await channel.set_qos(prefetch_count=1)
    queue = await channel.declare_queue(COMMENT_REPLY_QUEUE, durable=True)

    print(f"[*] Listening for comment-reply events on '{COMMENT_REPLY_QUEUE}'")
    try:
        async with queue.iterator() as queue_iter:
            async for message in queue_iter:
                async with message.process(ignore_processed=True):
                    try:
                        payload = CommentReplyPayload.parse_raw(message.body)
                    except (json.JSONDecodeError, ValidationError) as e:
                        logging.error(f"[CommentReply] Invalid message, discarding: {e}")
                        await message.reject(requeue=False)
                        continue

                    event = EventResponse(
                        event_type_response=7,
                        custom_event_type=None,
                        is_success=True,
                        message=payload.messageContent,
                        timestamp=payload.timestamp,
                        status="success"
                    )

                    sent_ws = await client_registry.send_to_client(
                        payload.recipientId,
                        event
                    )
                    try:
                        user_id_int = int(payload.recipientId)
                    except ValueError:
                        logging.error(f"[CommentReply] recipientId not an int: {payload.recipientId}")
                    else:
                        sent_push = await client_android_noti.send_notification(
                            send_to_id_user=user_id_int,
                            title=f"Reply from {payload.senderName}",
                            message=payload.messageContent
                        )

                    logging.info(f"[CommentReply] {payload.senderName} → {payload.recipientName}: {payload.messageContent}")
    except (asyncio.CancelledError, aio_pika.exceptions.ChannelClosed) as e:
        print(f"[Consumer] Shutting down: {e}")
    finally:
        await channel.close()
        await connection.close()