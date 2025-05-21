import asyncio
import logging
from pydantic import ValidationError
from repository.fcmtoken_mongo_repository import FcmTokenRepository
from models.mongo.models_mongo import FcmTokenModel
from .fcm_messaging import send_notification


class ClientAndroidNotifiacion:
    def __init__(self, fcm_token_repository : FcmTokenRepository):
        self.fcm_token_repository = fcm_token_repository

    async def send_notification(
        self,
        send_to_id_user: str,
        title: str,
        message: str
    ) -> bool:
        """
        Lookup the FCM token for `send_to_id_user`, validate it via Pydantic,
        and dispatch an Android notification without blocking the event loop.
        """
        try:
            raw = await self.fcm_token_repository.get_by_user_id(send_to_id_user)
            if raw is None:
                logging.warning(f"[AndroidNotif] No FCM record for user {send_to_id_user}")
                return False

            fcm_data = FcmTokenModel.parse_obj(raw)
        except ValidationError as ve:
            logging.error(f"[AndroidNotif] Invalid token document: {ve}")
            return False
        except Exception as e:
            logging.error(f"[AndroidNotif] Error fetching token: {e}")
            return False

        token = fcm_data.token

        loop = asyncio.get_running_loop()
        try:
            await loop.run_in_executor(
                None,
                send_notification,
                token,
                title,
                message
            )
            logging.info(f"[AndroidNotif] Notification sent to {send_to_id_user}")
            return True
        except Exception as e:
            logging.error(f"[AndroidNotif] Failed to send notification: {e}")
            return False