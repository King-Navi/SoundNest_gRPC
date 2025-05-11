import grpc
import jwt
import os
import logging
from dotenv import load_dotenv

load_dotenv()
JWT_SECRET = os.getenv("JWT_SECRET")

#/<package>.<Service>/<Method>
PUBLIC_METHODS = [
    '/song.SongService/DownloadSong',
    '/song.SongService/DownloadSongStream',
]

class JWTInterceptor(grpc.ServerInterceptor):
    def intercept_service(self, continuation, handler_call_details):
        logging.debug("JWT Interceptor...")
        print("Intercepted gRPC method:", handler_call_details.method)
        method_name = handler_call_details.method

        if method_name in PUBLIC_METHODS:
            return continuation(handler_call_details)

        metadata = dict(handler_call_details.invocation_metadata)
        token = metadata.get('authorization')

        if token is None or not token.startswith("Bearer "):
            return self._abort('Missing or invalid Authorization header')

        jwt_token = token.split(" ")[1]
        try:
            payload = jwt.decode(jwt_token, JWT_SECRET, algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            return self._abort('Token expired')
        except jwt.InvalidTokenError:
            return self._abort('Invalid token')

        handler = continuation(handler_call_details)

        if handler.unary_unary:
            def new_behavior(request, context):
                setattr(context, 'jwt_payload', payload)
                return handler.unary_unary(request, context)

            return grpc.unary_unary_rpc_method_handler(
                new_behavior,
                request_deserializer=handler.request_deserializer,
                response_serializer=handler.response_serializer
            )

        elif handler.unary_stream:
            def new_behavior(request, context):
                setattr(context, 'jwt_payload', payload)
                return handler.unary_stream(request, context)

            return grpc.unary_stream_rpc_method_handler(
                new_behavior,
                request_deserializer=handler.request_deserializer,
                response_serializer=handler.response_serializer
            )

        elif handler.stream_unary:
            def new_behavior(request_iterator, context):
                setattr(context, 'jwt_payload', payload)
                return handler.stream_unary(request_iterator, context)

            return grpc.stream_unary_rpc_method_handler(
                new_behavior,
                request_deserializer=handler.request_deserializer,
                response_serializer=handler.response_serializer
            )

        elif handler.stream_stream:
            def new_behavior(request_iterator, context):
                setattr(context, 'jwt_payload', payload)
                return handler.stream_stream(request_iterator, context)

            return grpc.stream_stream_rpc_method_handler(
                new_behavior,
                request_deserializer=handler.request_deserializer,
                response_serializer=handler.response_serializer
            )

        else:
            # Fallback: sin intervención
            return handler
    
    def _abort(self, message):
        def abort_behavior(request, context):
            context.abort(grpc.StatusCode.UNAUTHENTICATED, message)
        return grpc.unary_unary_rpc_method_handler(abort_behavior)
