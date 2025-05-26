import json
import aio_pika
import asyncio
from dotenv import load_dotenv
from utils.disk_access.song_file import SognFileManager
from repository.song_repository import SongRepository
from config.connection_rabbitmq import get_rabbitmq_url


load_dotenv()
QUEUE_NAME = "song.delete"
RABBITMQ_URL = get_rabbitmq_url()


async def process_deletion(id_song: int, file_manager : SognFileManager, song_repo : SongRepository):
    if id_song <= 0:
        raise ValueError("Invalid song ID")

    song = song_repo.get_song_by_id(id_song)
    if not song:
        raise ValueError("Song not found in database " + id_song)

    filename = song.fileName
    extension = song.SongExtension_.extensionName if song.SongExtension_ else None
    if not filename or not extension:
        raise ValueError("Incomplete song metadata")

    deleted = await file_manager.delete_file(filename, extension)
    if not deleted:
        raise FileNotFoundError("File not found on disk")

    success = song_repo.delete_song(id_song)
    if not success:
        raise RuntimeError("Failed to delete song from database")

    print(f"Song {id_song} deleted successfully.")

async def start_consumer(file_manager, song_repo):
    connection = await wait_for_rabbitmq(RABBITMQ_URL)
    channel = await connection.channel()
    await channel.set_qos(prefetch_count=1)

    queue = await channel.declare_queue(QUEUE_NAME, durable=True)

    async with queue.iterator() as queue_iter:
        print(f"[Consumer] Listening on '{QUEUE_NAME}'...")
        async for message in queue_iter:
            async with message.process(ignore_processed=True):
                try:
                    data = json.loads(message.body)
                    id_song = data.get("idSong")
                    if not id_song:
                        raise ValueError("Missing 'idSong'")
                    await process_deletion(id_song, file_manager, song_repo)
                except Exception as e:
                    print(f"[✗] Error processing message: {e}")
                    await message.reject(requeue=False)

#TODO: it goes in other file
async def wait_for_rabbitmq(url: str, retries: int = 60, delay: int = 1):
    for i in range(retries):
        try:
            return await aio_pika.connect_robust(url)
        except Exception as e:
            print(f"[RabbitMQ] Connection failed: {e}. Retrying in {delay}s...")
            await asyncio.sleep(delay)
    raise RuntimeError("RabbitMQ is not reachable after retries")