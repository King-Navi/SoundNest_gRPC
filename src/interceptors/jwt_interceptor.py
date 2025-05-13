import os
import logging
from grpc.aio import ServerInterceptor, ServicerContext
import jwt

from dotenv import load_dotenv
import grpc

load_dotenv()
JWT_SECRET = os.getenv("JWT_SECRET")

#/<package>.<Service>/<Method>
PUBLIC_METHODS = [
    '/song.SongService/DownloadSong',
    '/song.SongService/DownloadSongStream',
    '/event.EventService/Event', #TODO: REMOVE
]

class JWTInterceptor(ServerInterceptor):
    async def intercept_service(self, continuation, handler_call_details):
        logging.debug("JWT Interceptor...")
        print("Intercepted gRPC method:", handler_call_details.method)
        method_name = handler_call_details.method

        if method_name in PUBLIC_METHODS:
            return await continuation(handler_call_details)

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

        handler = await continuation(handler_call_details)
        if handler is None:
            return None
        
        # Envuelve según el tipo
        if handler.request_streaming and handler.response_streaming:
            async def new_behavior(request_iterator, context: ServicerContext):
                setattr(context, 'jwt_payload', payload)
                return await handler.stream_stream(request_iterator, context)
            return grpc.aio.stream_stream_rpc_method_handler(
                new_behavior,
                request_deserializer=handler.request_deserializer,
                response_serializer=handler.response_serializer
            )

        elif handler.request_streaming:
            async def new_behavior(request_iterator, context: ServicerContext):
                setattr(context, 'jwt_payload', payload)
                return await handler.stream_unary(request_iterator, context)
            return grpc.aio.stream_unary_rpc_method_handler(
                new_behavior,
                request_deserializer=handler.request_deserializer,
                response_serializer=handler.response_serializer
            )

        elif handler.response_streaming:
            async def new_behavior(request, context: ServicerContext):
                setattr(context, 'jwt_payload', payload)
                return await handler.unary_stream(request, context)
            return grpc.aio.unary_stream_rpc_method_handler(
                new_behavior,
                request_deserializer=handler.request_deserializer,
                response_serializer=handler.response_serializer
            )

        else:
            async def new_behavior(request, context: ServicerContext):
                setattr(context, 'jwt_payload', payload)
                return await handler.unary_unary(request, context)
            return grpc.aio.unary_unary_rpc_method_handler(
                new_behavior,
                request_deserializer=handler.request_deserializer,
                response_serializer=handler.response_serializer
            )
    
    def _abort(self, message):
        async def abort_behavior(request, context):
            context.abort(grpc.StatusCode.UNAUTHENTICATED, message)
        return grpc.aio.unary_unary_rpc_method_handler(abort_behavior)
