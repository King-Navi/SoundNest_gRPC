import grpc

#TODO: This is for education propose only 
class LoggerInterceptor(grpc.ServerInterceptor):
    def intercept_service(self, continuation, handler_call_details):
        handler = continuation(handler_call_details)

        def new_behavior(request, context):
            jwt_payload = getattr(context, 'jwt_payload', None)
            if jwt_payload:
                user_id = jwt_payload.get('id')
                username = jwt_payload.get('username')
                print(f"[LoggerInterceptor] Request from user {username} (ID: {user_id})")
            else:
                print("[LoggerInterceptor] Request without JWT payload")
            return handler.unary_unary(request, context)

        return grpc.unary_unary_rpc_method_handler(
            new_behavior,
            request_deserializer=handler.request_deserializer,
            response_serializer=handler.response_serializer,
        )
