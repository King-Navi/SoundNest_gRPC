import asyncio
import datetime
import grpc 
from event import event_pb2 , event_pb2_grpc
from dependency_injector.wiring import Provider, inject


from concurrent import futures


class EventController(event_pb2_grpc.EventServiceServicer):
    @inject
    def __init__(self):
        pass

    async def Event(self, request_iterator, context):
        queue = asyncio.Queue()

        async def read_from_client():
            try:
                async for req in request_iterator:
                    print(f"[Cliente {req.event_type}] Envió: {req.custom_event_type} - {req.payload}")
                    # Procesar o encolar respuesta si quieres responder basado en input
                    await queue.put(event_pb2.EventMessageReturn(
                        event_type_respose=req.event_type,
                        custom_event_type=req.custom_event_type,
                        is_succes_event=True,
                        message="Recibido y procesado desde cliente",
                        timestamp=datetime.datetime.utcnow().isoformat(),
                        status="ACK"
                    ))
            except grpc.aio.AioRpcError as e:
                print(f"Cliente se desconectó: {e.code()}")

        async def write_to_client():
            # Simula mensajes del servidor (por ejemplo, eventos automáticos)
            while True:
                await asyncio.sleep(5)
                msg = event_pb2.EventMessageReturn(
                    event_type_respose=event_pb2.EventType.NOTIFICATION,
                    custom_event_type="SERVER_ALERT",
                    is_succes_event=True,
                    message="Evento automático desde el servidor",
                    timestamp=datetime.datetime.utcnow().isoformat(),
                    status="OK"
                )
                await queue.put(msg)

        # Inicia lectura y generación en paralelo
        reader_task = asyncio.create_task(read_from_client())
        writer_task = asyncio.create_task(write_to_client())

        try:
            while True:
                msg = await queue.get()
                yield msg
        except asyncio.CancelledError:
            pass
        finally:
            reader_task.cancel()
            writer_task.cancel()
