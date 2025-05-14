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
from utils.check_connection import start_http_health_server
# pylint: enable=C0413
warnings.simplefilter("error", RuntimeWarning)
tracemalloc.start()
load_dotenv()
PORT = os.getenv("PYTHON_PORT")
ENVIROMENT = os.getenv("ENVIROMENT", "production")
async def serve(): # pylint: disable=C0116
    if ENVIROMENT == "development":
        logging.basicConfig(level=logging.DEBUG)
        logging.debug("Enter debug mode...")
        threading.Thread(target=start_http_health_server, daemon=True).start()

    container = Container()
    container.wire(modules=[
        "controller.user_controller",
        "controller.song_controller"
        # otros módulos que tengan Provide[]
    ])
    server =  aio.server(
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
    event_pb2_grpc.add_EventServiceServicer_to_server(event_controller, server)
    song_pb2_grpc.add_SongServiceServicer_to_server(song_controller, server)
    user_image_pb2_grpc.add_UserImageServiceServicer_to_server( user_image_controller, server)
    
    server.add_insecure_port(f'[::]:{PORT}')
    await server.start()
    print(f'gRPC server running on port {PORT}...')
    try:
        await server.wait_for_termination()
    except asyncio.CancelledError:
        pass
    finally:
        print("Shutting down gRPC server…")
        await server.stop(0)

if __name__ == '__main__':
    try:
        asyncio.run(serve())
    except KeyboardInterrupt:
        pass
