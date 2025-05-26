import os
import json
import logging
from datetime import datetime
import asyncio
import aio_pika
from dotenv import load_dotenv
from pydantic import BaseModel, Field, ValidationError
from config.connection_rabbitmq import get_rabbitmq_url
from controller.utils.client_registry import ClientRegistry 
from utils.wrappers.event_wrapper import EventResponse
from messaging.delete_song_consumer import wait_for_rabbitmq
from ..android_messaging import ClientAndroidNotifiacion

load_dotenv()

RABBITMQ_URL = get_rabbitmq_url()
SONG_VISITS_QUEUE = os.getenv("SONG_VISITS_QUEUE_NAME")

class SongVisitPayload(BaseModel):
    userId: int = Field(..., description="ID of the song’s owner")
    userName: str = Field(..., description="Name of the song’s owner")
    songId: int = Field(..., description="ID of the song")
    songName: str = Field(..., description="Name of the song")
    visitCount: int = Field(..., gt=0, description="Number of visits the song has")
    timestamp: datetime

async def start_consumer_song_visits(
    client_registry: ClientRegistry,
    client_android_noti: ClientAndroidNotifiacion
):
    connection = await wait_for_rabbitmq(RABBITMQ_URL)
    channel = await connection.channel()
    await channel.set_qos(prefetch_count=1)
    queue = await channel.declare_queue(SONG_VISITS_QUEUE, durable=True)
    print(f"[*] Listening for song-visit events on '{SONG_VISITS_QUEUE}'")
    try:
        async with queue.iterator() as queue_iter:
            async for message in queue_iter:
                async with message.process(ignore_processed=True):
                    try:
                        payload = SongVisitPayload.parse_raw(message.body)
                    except (json.JSONDecodeError, ValidationError) as e:
                        logging.error(f"[SongVisits] Invalid message, discarding: {e}")
                        await message.reject(requeue=False)
                        continue
                    event_msg = (
                        f"Your song “{payload.songName}” reached {payload.visitCount} plays."
                    )
                    event = EventResponse(
                        event_type_response=8,
                        custom_event_type=None,
                        is_success=True,
                        message=event_msg,
                        timestamp=payload.timestamp,
                        status="success"
                    )
                    sent_ws = await client_registry.send_to_client(
                        payload.userId,
                        event
                    )
                    try:
                        user_id_int = int(payload.userId)
                    except ValueError:
                        logging.error(f"[SongVisits] userId not an int: {payload.userId}")
                    else:
                        sent_push = await client_android_noti.send_notification(
                            send_to_id_user=user_id_int,
                            title="Song Play Milestone",
                            message=event_msg
                        )

                    logging.info(f"[SongVisits] {payload.userName} → “{payload.songName}”: {payload.visitCount} plays")
    except (asyncio.CancelledError, aio_pika.exceptions.ChannelClosed) as e:
        print(f"[Consumer] Shutting down: {e}")
    finally:
        await channel.close()
        await connection.close()