# pylint: disable=C0413
import os, sys# pylint: disable=C0410
import warnings
import tracemalloc
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "generated"))
import logging
import threading
import asyncio
from grpc import aio
from dotenv import load_dotenv
from event import event_pb2_grpc
from streaming import song_pb2_grpc
from user_photo import user_image_pb2_grpc
from interceptors.jwt_interceptor import JWTInterceptor
from utils.injection.containers import Container
from messaging.delete_song_consumer import start_consumer
from messaging.alertEvent.comment_reply_consumer import start_consumer_comment_reply
from messaging.alertEvent.song_visits_consumer import start_consumer_song_visits
# pylint: enable=C0413
warnings.simplefilter("error", RuntimeWarning)
tracemalloc.start()
load_dotenv()
PORT = os.getenv("PYTHON_PORT")
ENVIROMENT = os.getenv("ENVIROMENT", "production")
async def serve():
    if ENVIROMENT == "development":
        logging.basicConfig(level=logging.INFO)
        logging.info("Enter info mode...")
    container = Container()
    container.wire()
    grpc_server =  aio.server(
        options=[
            ('grpc.max_send_message_length', 100 * 1024 * 1024),  # 100 MB
            ('grpc.max_receive_message_length', 100 * 1024 * 1024)
        ]
        ,
        interceptors=[JWTInterceptor()]
    )
    event_controller = container.event_controller()
    user_image_controller = container.user_image_controller()
    song_controller = container.song_file_controller()
    event_pb2_grpc.add_EventServiceServicer_to_server(event_controller, grpc_server)
    song_pb2_grpc.add_SongServiceServicer_to_server(song_controller, grpc_server)
    user_image_pb2_grpc.add_UserImageServiceServicer_to_server( user_image_controller, grpc_server)

    grpc_server.add_insecure_port(f'[::]:{PORT}')
    await grpc_server.start()
    print(f'gRPC server running on port {PORT}...')
    try:
        await asyncio.gather(
            grpc_server.wait_for_termination(),
            start_consumer(container.song_file_manager(), container.song_repository()),
            start_consumer_song_visits(container.client_registry(), container.client_msg_android()),
            start_consumer_comment_reply(container.client_registry(), container.client_msg_android()),
        )
    except asyncio.CancelledError:
        pass
    finally:
        print("Shutting down gRPC server…")
        await grpc_server.stop(0)

if __name__ == '__main__':
    try:
        asyncio.run(serve())
    except KeyboardInterrupt:
        pass
