import grpc
import os
import contextvars
import jwt
from dotenv import load_dotenv
from grpc.aio import ServerInterceptor
from grpc import StatusCode
from grpc import RpcMethodHandler
load_dotenv()
JWT_SECRET = os.getenv("JWT_SECRET")

#/<package>.<Service>/<Method>
PUBLIC_METHODS = [
    '/song.SongService/DownloadSong',
    '/song.SongService/DownloadSongStream',
]

# ContextVar para propagar el payload
_JWT_PAYLOAD = contextvars.ContextVar("jwt_payload")

class JWTInterceptor(ServerInterceptor):
    async def intercept_service(self, continuation, handler_call_details):
        if handler_call_details.method in PUBLIC_METHODS:
            return await continuation(handler_call_details)

        handler = await continuation(handler_call_details)
        if handler is None:
            return None
        async def _validate_and_set(context):
            md = dict(context.invocation_metadata())
            auth = md.get("authorization", "")
            if not auth.startswith("Bearer "):
                await context.abort(StatusCode.UNAUTHENTICATED,
                              "Missing or invalid Authorization header")
            token = auth.split(" ", 1)[1]
            try:
                payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
            except jwt.ExpiredSignatureError:
                await context.abort(StatusCode.UNAUTHENTICATED, "Token expired")
            except jwt.InvalidTokenError:
                await context.abort(StatusCode.UNAUTHENTICATED, "Invalid token")

            _JWT_PAYLOAD.set(payload)

        
        if not handler.request_streaming and not handler.response_streaming:
            async def unary_unary_wrapper(request, context):
                await _validate_and_set(context)
                return await handler.unary_unary(request, context)

            return grpc.unary_unary_rpc_method_handler(
                unary_unary_wrapper,
                request_deserializer=handler.request_deserializer,
                response_serializer=handler.response_serializer,
            )
        if not handler.request_streaming and handler.response_streaming:
            async def unary_stream_wrapper(request, context):
                await _validate_and_set(context)
                async for resp in handler.unary_stream(request, context):
                    yield resp

            return grpc.unary_stream_rpc_method_handler(
                unary_stream_wrapper,
                request_deserializer=handler.request_deserializer,
                response_serializer=handler.response_serializer,
            )
        if handler.request_streaming and not handler.response_streaming:
            async def stream_unary_wrapper(request_iterator, context):
                await _validate_and_set(context)
                return await handler.stream_unary(request_iterator, context)

            return grpc.stream_unary_rpc_method_handler(
                stream_unary_wrapper,
                request_deserializer=handler.request_deserializer,
                response_serializer=handler.response_serializer,
            )
        if handler.request_streaming and handler.response_streaming:
            async def stream_stream_wrapper(request_iterator, context):
                await _validate_and_set(context)
                async for resp in handler.stream_stream(request_iterator, context):
                    yield resp

            return grpc.stream_stream_rpc_method_handler(
                stream_stream_wrapper,
                request_deserializer=handler.request_deserializer,
                response_serializer=handler.response_serializer,
            )
        return handler
