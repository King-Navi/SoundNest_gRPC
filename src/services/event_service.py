import datetime
import logging
import json
from pydantic import ValidationError
from .models.event import CommentReplyModel
from dependency_injector.wiring import Provider, inject
from utils.wrappers.event_wrapper import IncomingEvent , RouterResponse , EventResponse
from typing import Callable, Awaitable, Dict

from messaging.notification_producer import publish_notification
class EventService:
    """business-logic layer for all SongService RPCs."""
    _handlers: Dict[int, Callable[[int, str, IncomingEvent], Awaitable[RouterResponse]]]
    @inject
    def __init__(self):
        self._handlers = {
            0: self._handle_unknown,
            1: self._handle_unknown,
            2: self._handle_notification,
            3: self._handle_unknown,
            4: self._handle_handshake_start,
            5: self._handle_handshake_end,
            6: self._handle_comment_reply_send,
            7: self._handle_comment_reply_recive,
            8: self._handle_song_visit_notification,

            # TODO: agregar mas
        }
    async def process_event(self,user_id: int, user_name: str, event: IncomingEvent) -> RouterResponse:
        handler = self._handlers.get(event.event_type, self._handle_unknown)
        return await handler(user_id, user_name, event)

    async def _handle_handshake_start(self,user_id: int, user_name: str, event: IncomingEvent) -> RouterResponse:
        logging.info(f"Handshake para: {user_name}" )
        return None

    async def _handle_handshake_end(self,user_id: int, user_name: str, event: IncomingEvent) -> RouterResponse:
        logging.info(f"Handshake despedida: {user_name}" )
        return None

    async def _handle_notification(self,user_id: int, user_name: str, event: IncomingEvent) -> RouterResponse:
        pass

    async def _handle_comment_reply_send(self,user_id: int, user_name: str, event: IncomingEvent) -> RouterResponse:
        print(f"[WARN] reply_recive event:")
        try:
            raw_payload = json.loads(event.payload)
            comment_reply = CommentReplyModel(**raw_payload)
            print(f"[DEBUG] Valid payload: {comment_reply}")
            await publish_notification({
                "title": "Respondieron tu comentario",
                "sender": f"{user_name}",
                "user_id": f"{comment_reply.id_author}",
                "notification": f"Alguien ha respondido tu cometnario: {comment_reply.message}",
                "relevance": "low"
            })
            return RouterResponse(
                send_to_id_user=comment_reply.id_author,
                response=EventResponse(
                    event_type_response= 7, #COMMENT_REPLY_RECIVE
                    custom_event_type=event.custom_event_type,
                    is_success=True,
                    message="Reply received",
                    status="OK",
                    timestamp=datetime.datetime.utcnow().isoformat()
                )
            )

        except (json.JSONDecodeError, ValidationError) as e:
            print(f"[ERROR] Invalid payload: {e}")

            return RouterResponse(
                send_to_id_user=user_id,
                response=EventResponse(
                    event_type_response=event.event_type,
                    custom_event_type=event.custom_event_type,
                    is_success=False,
                    message="Invalid payload",
                    status="FAIL",
                    timestamp=datetime.datetime.utcnow().isoformat()
                )
            )
    
    async def _handle_comment_reply_recive(self,user_id: int, user_name: str, event: IncomingEvent) -> RouterResponse:
        #TODO: Procesar el incoming
        print(f"[WARN] reply_recive event:")

    async def _handle_song_visit_notification(self,user_id: int, user_name: str, event: IncomingEvent) -> RouterResponse:
        return RouterResponse(
            send_to_id_user=int(user_id),
            response=EventResponse(
                event_type_response=event.event_type,
                custom_event_type=event.custom_event_type,
                is_success=False,
                message="NOT_SUPPORTED",
                status="FAIL",
                timestamp=datetime.datetime.utcnow().isoformat()
            )
        )

    async def _handle_unknown(self,user_id: int, user_name: str, event: IncomingEvent) -> RouterResponse:
        print(f"[WARN] unknown event:")
        return RouterResponse(
            send_to_id_user=int(user_id),
            response=EventResponse(
                event_type_response=event.event_type,
                custom_event_type=event.custom_event_type,
                is_success=False,
                message="NOT_SUPPORTED",
                status="FAIL",
                timestamp=datetime.datetime.utcnow().isoformat()
            )
        )
