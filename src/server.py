import os, sys
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
# from interceptors.jwt_interceptor import JWTInterceptor
# from interceptors.logger_interceptor import LoggerInterceptor
from utils.injection.containers import Container

from utils.check_connection import start_http_health_server

load_dotenv()
PORT = os.getenv("PYTHON_PORT")
CERT_PATH = os.getenv("TLS_CRT_PATH")
KEY_PATH = os.getenv("TLS_KEY_PATH")
ENVIROMENT = os.getenv("ENVIROMENT", "production")
def serve(): # pylint: disable=C0116
    server = grpc.server(
        futures.ThreadPoolExecutor(max_workers=10)
        #,
        #interceptors=[JWTInterceptor(), LoggerInterceptor()]
    )
    song_pb2_grpc.add_SongServiceServicer_to_server(SongService(), server)
    user_image_pb2_grpc.add_UserImageServiceServicer_to_server( UserImageController(), server)
    with open(KEY_PATH, 'rb') as f:
        private_key = f.read()
    with open(CERT_PATH, 'rb') as f:
        certificate = f.read()
    server_credentials = grpc.ssl_server_credentials(((private_key, certificate),))
    server.add_secure_port(f'[::]:{PORT}', server_credentials)
    server.start()
    print(f'gRPC server running on port {PORT}...')

    def shutdown(signum, frame): # pylint: disable=W0613
        print("Shutting down gRPC server...")
        server.stop(0)
        sys.exit(0)

    signal.signal(signal.SIGINT, shutdown)
    signal.signal(signal.SIGTERM, shutdown)

    server.wait_for_termination()


def initialize():
    container = Container()
    container.wire(modules=[
        "controllers.user_controller"
        # otros módulos que tengan Provide[]
    ])

    if ENVIROMENT == "development":
        threading.Thread(target=start_http_health_server, daemon=True).start()

    serve()

if __name__ == '__main__':
    if not PORT or not CERT_PATH or not KEY_PATH:
        raise RuntimeError("Variables de entorno no definidas correctamente.")
    initialize()
