import datetime
from dataclasses import dataclass


@dataclass
class IncomingEvent:
    """
    Represents an incoming event received by the system.

    Attributes:
        event_type (int): Numeric code indicating the type of the event.
        custom_event_type (str): Custom string identifier for event types.
        payload (str): The raw event data payload.
    """
    event_type: int
    custom_event_type: str
    payload: str

@dataclass
class EventResponse:
    """
    Defines the response generated for an event.

    Attributes:
        event_type_response (int): Numeric code of the response event type.
        custom_event_type (str): Custom string identifier for the response type.
        is_success (bool): Whether the event was processed successfully.
        message (str): Human-readable message describing the outcome.
        status (str): Status code or description for the response.
        timestamp (str): ISO 8601 UTC timestamp when the response was created.
    event_type_response:
        UNKNOWN = 0;
        CUSTOM = 1;
        NOTIFICATION = 2;
        DATA_UPDATE = 3;
        HANDSHAKE_START =4;
        HANDSHAKE_FINISH = 5;
        COMMENT_REPLY_SEND = 6;
        COMMENT_REPLY_RECIVE = 7;
        SONG_VISITS_NOTIFICATION = 8;
    """
    event_type_response: int
    custom_event_type: str
    is_success: bool
    message: str
    status: str
    timestamp: str = datetime.datetime.utcnow().isoformat()

@dataclass
class RouterResponse:
    """
    Represents a response routed to a specific user.

    Attributes:
        send_to_id_user (int): The ID of the user to whom this response should be sent.
        response (EventResponse): The action or event response to deliver.
    """
    send_to_id_user : int
    response : EventResponse
