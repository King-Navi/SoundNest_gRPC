import asyncio
import datetime
import grpc
import logging
from event import event_pb2, event_pb2_grpc
from dependency_injector.wiring import Provider, inject
from services.event_service import EventService
from interceptors.jwt_interceptor import _JWT_PAYLOAD
from utils.wrappers.event_wrapper import IncomingEvent, RouterResponse , EventResponse
from .utils.client_registry import ClientRegistry , ActiveClient
from messaging.android_messaging import ClientAndroidNotifiacion

PING_TYPE = 3
class EventController(event_pb2_grpc.EventServiceServicer):
    @inject
    def __init__(self,
                 event_service : EventService = Provider["event_service"],
                 client_registry: ClientRegistry= Provider["client_registry"],
                 client_msg_android: ClientAndroidNotifiacion= Provider["client_msg_android"]):
        self.event_service = event_service
        self.client_registry = client_registry
        self.client_msg_android = client_msg_android

    async def Event(self, request_iterator, context):
        queue = asyncio.Queue()
        jwt_payload = _JWT_PAYLOAD.get(None)
        if not jwt_payload:
            await context.abort(grpc.StatusCode.UNAUTHENTICATED, "Missing authentication token")
        user_id = jwt_payload.get('id')
        username = jwt_payload.get('username')
        client = ActiveClient(
            user_id=user_id,
            user_name=username,
            queue=queue,
            context=context,
        )
        await self.client_registry.register(client)
        cancel_event = asyncio.Event()

        async def read_from_client():
            try:
                async for req in request_iterator:
                    if req.event_type == PING_TYPE:
                        logging.info(f"Ignorado evento tipo 3 (PONG) de {user_id}")
                        continue
                    logging.info(f"[Cliente id: {user_id}  Nombre: {username}] Tipo:{req.event_type} Envió: {req.custom_event_type} - {req.payload}")
                    incoming = IncomingEvent(
                        event_type=req.event_type,
                        custom_event_type=req.custom_event_type,
                        payload=req.payload
                    )
                    result : RouterResponse = await self.event_service.process_event(user_id,username,incoming)
                    if result is None:
                        continue
                    await self.client_msg_android.send_notification(send_to_id_user=result.send_to_id_user, title="Te ha llegado un mensaje", message=result.response)
                    await self.client_registry.send_to_client(result.send_to_id_user , result.response)

            except grpc.aio.AioRpcError as e:
                logging.info(f"[ERROR] Cliente se desconectó: {e.code()}")
            except Exception as e:
                logging.info(f"[ERROR] Fallo en read_from_client: {e}")
            finally:
                cancel_event.set()

        async def ping_to_client():
            try:
                while not cancel_event.is_set():
                    await asyncio.sleep(30)
                    msg = EventResponse(
                        event_type_response=PING_TYPE,
                        custom_event_type="PING",
                        is_success=True,
                        message="PING",
                        timestamp=datetime.datetime.utcnow().isoformat(),
                        status="PING"
                    )
                    success = await self.client_registry.send_to_client(user_id, msg)
                    if not success:
                        logging.info("[WARN] Cliente inactivo, cancelando ping_to_client.")
                        cancel_event.set()
            except Exception as e:
                logging.info(f"[ERROR] Fallo en ping_to_client: {e}")
                cancel_event.set()

                

        reader_task = asyncio.create_task(read_from_client())
        writer_task = asyncio.create_task(ping_to_client())

        try:
            while not cancel_event.is_set():
                get_msg_task    = asyncio.create_task(queue.get())
                cancel_evt_task = asyncio.create_task(cancel_event.wait())

                done, pending = await asyncio.wait(
                    [get_msg_task, cancel_evt_task],
                    return_when=asyncio.FIRST_COMPLETED,
                )
                for task in pending:
                    task.cancel()
                if cancel_evt_task in done:
                    break
                msg = get_msg_task.result()
                yield msg
        except Exception as e:
            logging.info(f"[ERROR] Fallo en stream principal: {e}")
        finally:
            reader_task.cancel()
            writer_task.cancel()
            await asyncio.gather(reader_task, writer_task, return_exceptions=True)
            await self.client_registry.unregister(user_id, client)
            logging.info(f"[INFO] Cliente {user_id} desconectado y removido.")
