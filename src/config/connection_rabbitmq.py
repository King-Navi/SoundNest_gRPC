import os

def get_rabbitmq_url() -> str:
    protocol = os.getenv("RABBITMQ_PROTOCOL", "amqp")
    user = os.getenv("RABBITMQ_USER", "guest")
    password = os.getenv("RABBITMQ_PASSWORD", "guest")
    host = os.getenv("RABBITMQ_HOST", "localhost")
    port = os.getenv("RABBITMQ_PORT", "5672")
    vhost = os.getenv("RABBITMQ_VHOST", "/")

    from urllib.parse import quote
    encoded_vhost = quote(vhost, safe='')

    return f"{protocol}://{user}:{password}@{host}:{port}/{encoded_vhost}"
