import os
from dependency_injector import containers, providers
from dotenv import load_dotenv

from repository.song_repository import SongRepository
from repository.song_extension_repository import SongExtensionRepository
from repository.photo_repository import PhotoRepository
from repository.fcmtoken_mongo_repository import FcmTokenRepository
from messaging.android_messaging import ClientAndroidNotifiacion
from utils.disk_access.user_image import UserImageManager
from utils.disk_access.song_file import SognFileManager
from config.connection_mysql import SessionLocal
from config.connection_mongo import db as mongo_db

load_dotenv()

MONGO_COLLECTION_COMMENTS = os.getenv("MONGO_COLLECTION_COMMENTS", "comments")
MONGO_COLLECTION_ADDITIONAL_INFO = os.getenv("MONGO_COLLECTION_ADDITIONAL_INFO", "additional_info")
MONGO_COLLECTION_NOTIFICATIONS = os.getenv("MONGO_COLLECTION_NOTIFICATIONS", "notifications")
MONGO_COLLECTION_FCM_TOKENS = os.getenv("MONGO_COLLECTION_FCM_TOKENS", "fcm_tokens")

PATH_SONG = os.getenv("SONGS_PATH")
USER_IMAGE_PATH = os.getenv("USER_IMAGE_PATH")

class BaseContainer(containers.DeclarativeContainer):
    mongo_db_provider = providers.Object(mongo_db)
    session_provider = providers.Factory(SessionLocal)
    comments_collection = providers.Object(mongo_db[MONGO_COLLECTION_COMMENTS])
    additional_info_collection = providers.Object(mongo_db[MONGO_COLLECTION_ADDITIONAL_INFO])
    notifications_collection = providers.Object(mongo_db[MONGO_COLLECTION_NOTIFICATIONS])
    fcm_tokens_collection = providers.Object(mongo_db[MONGO_COLLECTION_FCM_TOKENS])

    user_image_manager = providers.Singleton(UserImageManager, base_dir=USER_IMAGE_PATH)
    song_file_manager = providers.Singleton(SognFileManager, base_dir=PATH_SONG)

    fcm_token_repository = providers.Factory(
        FcmTokenRepository,
        collection=fcm_tokens_collection
    )
    song_extension_repository = providers.Factory(
        SongExtensionRepository,
        session=providers.Callable(session_provider)
    )
    song_repository = providers.Factory(
        SongRepository,
        session=providers.Callable(session_provider)
    )
    photo_repository = providers.Factory(
        PhotoRepository,
        session=providers.Callable(session_provider)
    )

    client_msg_android = providers.Factory(
        ClientAndroidNotifiacion,
        fcm_token_repository
    )

