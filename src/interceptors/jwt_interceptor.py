import grpc
import jwt
import os
from dotenv import load_dotenv

load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")

#/<package>.<Service>/<Method>
PUBLIC_METHODS = [
    '/soundnest.FileUploader/PublicMethod',
]

class JWTInterceptor(grpc.ServerInterceptor):
    def intercept_service(self, continuation, handler_call_details):
        method_name = handler_call_details.method

        if method_name in PUBLIC_METHODS:
            #lo dejamos pasar sin validar JWT
            return continuation(handler_call_details)     
        metadata = dict(handler_call_details.invocation_metadata)
        token = metadata.get('authorization')

        if token is None or not token.startswith("Bearer "):
            return self._abort('Missing or invalid Authorization header')

        jwt_token = token.split(" ")[1]
        try:
            payload = jwt.decode(jwt_token, SECRET_KEY, algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            return self._abort('Token expired')
        except jwt.InvalidTokenError:
            return self._abort('Invalid token')

        handler = continuation(handler_call_details)

        def new_behavior(request, context):
            setattr(context, 'jwt_payload', payload)
            return handler.unary_unary(request, context)

        return grpc.unary_unary_rpc_method_handler(
            new_behavior,
            request_deserializer=handler.request_deserializer,
            response_serializer=handler.response_serializer,
        )
    
    def _abort(self, message):
        def abort_behavior(request, context):
            context.abort(grpc.StatusCode.UNAUTHENTICATED, message)
        return grpc.unary_unary_rpc_method_handler(abort_behavior)
