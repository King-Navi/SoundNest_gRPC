import asyncio
import logging
import asyncio

from dataclasses import dataclass
from grpc.aio import ServicerContext
from event.event_pb2 import EventMessageReturn #pylint: disable=E0611
from utils.wrappers.event_wrapper import EventResponse

@dataclass
class ActiveClient:
    user_id: str
    user_name: str
    queue: asyncio.Queue
    context: ServicerContext


class ClientRegistry:
    def __init__(self):
        self._clients: dict[str, ActiveClient] = {}
        self._lock = asyncio.Lock()

    async def register(self, client: ActiveClient):
        logging.info(f"Se registro: {client.user_name}" )
        async with self._lock:
            self._clients[client.user_id] = client

    async def unregister(self, user_id: str):
        logging.info(f"Se elimino del directorio el id: {user_id}" )
        async with self._lock:
            self._clients.pop(user_id, None)

    async def get(self, user_id: str) -> ActiveClient | None:
        async with self._lock:
            return self._clients.get(user_id)

    async def send_to_client(self, user_id: str, event: EventResponse) -> bool:
        """
        Send an event notification to a registered client.
        
        This method looks up the ActiveClient associated with the given user_id,
        constructs an EventMessageReturn from the provided EventResponse, and enqueues
        it onto the client's asyncio.Queue. Access to the internal client registry
        is guarded by an asyncio.Lock to ensure thread-safe modifications.

        If no client is found for the given user_id, or if the client's gRPC
        ServicerContext has been marked as done (closed/cancelled), the client
        entry is removed from the registry and the method returns False.

        Args:
            user_id (str): Identifier of the target client.
            message (EventResponse): The event payload to send.

        Returns:
            bool: 
                - True if the message was successfully enqueued for delivery.
                - False if the client was missing or its context is no longer active.
        """
        logging.info(
            f"[ClientRegistry] Sending event '{event.event_type_response}' to user {user_id}"
        )
        ts_value = (
            event.timestamp
            if isinstance(event.timestamp, str)
            else event.timestamp.isoformat()
        )
        proto_msg = EventMessageReturn(
            event_type_respose = event.event_type_response,
            custom_event_type = event.custom_event_type or "",
            is_succes_event = event.is_success,
            message = event.message,
            timestamp = ts_value,
            status = event.status or ""
        )
        async with self._lock:
            client = self._clients.get(user_id)
            if not client or client.context.done():
                logging.warning(f"Could not send to {user_id}: client missing or context done")
                self._clients.pop(user_id, None)
                return False
            await client.queue.put(proto_msg)
            return True

    async def list_clients(self) -> list[str]:
        async with self._lock:
            logging.info(f"[ClientRegistry] Clientes conectados: {list(self._clients.keys())}")
            return list(self._clients.keys())
