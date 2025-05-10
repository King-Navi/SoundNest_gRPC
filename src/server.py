import os, sys
import logging
#TODO: Esto es una porqueria considera migrar src/generated/streaming -> src/streaming
SRC_DIR = os.path.dirname(__file__)# directorio src/generated
GENERATED = os.path.join(SRC_DIR, "generated")
# Mete src/generated al frente de sys.path
sys.path.insert(0, GENERATED)
from concurrent import futures
import threading, signal, sys as _sys
import grpc
from dotenv import load_dotenv
from streaming import song_pb2_grpc
from user_photo import user_image_pb2_grpc
from http.server import HTTPServer
from services.song_service import SongService
from controller.user_controller import UserImageController
from interceptors.jwt_interceptor import JWTInterceptor
from utils.injection.containers import Container

from utils.check_connection import start_http_health_server

load_dotenv()
PORT = os.getenv("PYTHON_PORT")
ENVIROMENT = os.getenv("ENVIROMENT", "production")
def serve(): # pylint: disable=C0116
    container = Container()
    container.wire(modules=[
        "controller.user_controller"
        # otros módulos que tengan Provide[]
    ])
    server = grpc.server(
        futures.ThreadPoolExecutor(max_workers=10)
        ,
        interceptors=[JWTInterceptor()]
    )
    user_image_controller = container.user_image_controller()
    song_controller = container.song_file_controller()
    song_pb2_grpc.add_SongServiceServicer_to_server(song_controller, server)
    user_image_pb2_grpc.add_UserImageServiceServicer_to_server( user_image_controller, server)
    server.add_insecure_port(f'[::]:{PORT}')

    server.start()
    print(f'gRPC server running on port {PORT}...')
    if ENVIROMENT == "development":
        logging.debug("Enter development mode...")
        def shutdown(signum, frame): # pylint: disable=W0613
            print("Shutting down gRPC server...")
            server.stop(0)
            sys.exit(0)
        signal.signal(signal.SIGINT, shutdown)
        signal.signal(signal.SIGTERM, shutdown)
    server.wait_for_termination()

def initialize():
    if ENVIROMENT == "development":
        logging.basicConfig(level=logging.DEBUG)
        threading.Thread(target=start_http_health_server, daemon=True).start()
    serve()

if __name__ == '__main__':
    initialize()
