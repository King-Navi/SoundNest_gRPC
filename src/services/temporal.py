import grpc
from concurrent import futures
from queue import Queue
import threading
import time

from event import events_pb2, events_pb2_grpc

# ---- Shared state ----
# List of (Queue, filter_set) tuples for all active subscribers
_subscribers = []
_sub_lock = threading.Lock()

def broadcast_event(event: events_pb2.EventNotification):
    """Push this event to every subscriber whose filters match."""
    with _sub_lock:
        # copy list so it's safe if someone unsubscribes mid-loop
        for queue, filters in list(_subscribers):
            if not filters or event.event_type in filters:
                queue.put(event)

def event_producer():
    """Background thread: simulate server-side events continuously."""
    while True:
        time.sleep(5)  # pretend we got something every 5s
        evt = events_pb2.EventNotification(
            event_type="NEW_MESSAGE",
            timestamp=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            payload_json='{"message":"Hello subscribers!"}'
        )
        broadcast_event(evt)

# start the producer as soon as the module is imported
threading.Thread(target=event_producer, daemon=True).start()


class EventService(events_pb2_grpc.EventServiceServicer):
    """Handles client subscriptions via server-streaming RPC."""

    def Subscribe(self, request, context):
        """
        RPC type: unary request, server-streaming response.
        - request: SubscribeRequest (session_id: string, event_types: [string])
        - yields: EventNotification
        """
        # Each client gets its own queue
        q: Queue[events_pb2.EventNotification] = Queue()
        filters = set(request.event_types)
        # register this subscriber
        with _sub_lock:
            _subscribers.append((q, filters))

        try:
            print(f"Client {request.session_id} subscribed; filters={filters or 'all'}")
            # keep streaming until client cancels
            while True:
                event = q.get()              # blocks until producer calls put()
                yield event                  # push down the gRPC stream
        except grpc.RpcError:
            # Happens when client disconnects or cancels
            print(f"Client {request.session_id} disconnected")
        finally:
            # cleanup
            with _sub_lock:
                _subscribers.remove((q, filters))

