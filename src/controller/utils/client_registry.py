import asyncio
import logging
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

    def __hash__(self):
        return hash(id(self))

    def __eq__(self, other):
        return self is other

class ClientRegistry:
    def __init__(self):
        self._clients: dict[str, set[ActiveClient]] = {}
        self._lock = asyncio.Lock()

    async def register(self, client: ActiveClient):
        async with self._lock:
            if client.user_id not in self._clients:
                self._clients[client.user_id] = set()
            self._clients[client.user_id].add(client)
            logging.info(f"Registrado cliente {client.user_name} con ID {client.user_id}. Total conexiones: {len(self._clients[client.user_id])}")

    async def unregister(self, user_id: str, client_to_remove: ActiveClient):
        async with self._lock:
            clients = self._clients.get(user_id)
            if clients:
                clients.discard(client_to_remove)
                logging.info(f"Cliente {client_to_remove.user_name} eliminado de ID {user_id}. Quedan: {len(clients)} conexiones")
                if not clients:
                    del self._clients[user_id]

    async def get(self, user_id: str) -> set[ActiveClient] | None:
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
        proto_msg = EventMessageReturn(
                event_type_respose=event.event_type_response,
                custom_event_type=event.custom_event_type or "",
                is_succes_event=event.is_success,
                message=event.message,
                timestamp=event.timestamp if isinstance(event.timestamp, str) else event.timestamp.isoformat(),
                status=event.status or ""
        )

        async with self._lock:
            clients = self._clients.get(user_id, set()).copy()
            if not clients:
                logging.warning(f"No se encontraron clientes activos para el usuario {user_id}")
                return False
            
            inactive = {c for c in clients if c.context.done()}
            active = clients - inactive
            if inactive:
                self._clients[user_id] -= inactive
                if not self._clients[user_id]:
                    del self._clients[user_id]
        sent = False
        for client in active:
            await client.queue.put(proto_msg)
            sent = True
        if sent:
            logging.info(f"[ClientRegistry] Sent '{event.event_type_response}' to user {user_id} ({len(active)} clientes)")
        return sent

    async def list_clients(self) -> list[str]:
        async with self._lock:
            return [f"{uid} ({len(clients)} conexiones)" for uid, clients in self._clients.items()]
