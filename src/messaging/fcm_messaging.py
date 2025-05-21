from firebase_admin import messaging
import config.fcm_config

def send_notification(token: str, title: str, body: str):
    message = messaging.Message(
        notification=messaging.Notification(
            title=title,
            body=body
        ),
        token=token
    )

    try:
        response = messaging.send(message)
        print("Notificación enviada:", response)
    except Exception as e:
        print("Error al enviar notificación:", e)
