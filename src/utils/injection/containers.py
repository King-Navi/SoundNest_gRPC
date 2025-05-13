import os
from dependency_injector import containers, providers
from dotenv import load_dotenv

from repository.photo_repository import PhotoRepository
from repository.song_repository import SongRepository
from repository.song_extension_repository import SongExtensionRepository
from controller.event_controller import EventController
from controller.user_controller import UserImageController
from controller.song_controller import SongController
from services.user_images_service import UserImageService
from services.song_service import SongService
from utils.disk_access.user_image import UserImageManager
from utils.disk_access.song_file import SognFileManager
from config.connection_mysql import SessionLocal
from config.connection_mongo import db as mongo_db

load_dotenv()
MONGO_COLLECTION_COMMENTS = os.getenv("MONGO_COLLECTION_COMMENTS", "comments")
MONGO_COLLECTION_ADDITIONAL_INFO = os.getenv("MONGO_COLLECTION_ADDITIONAL_INFO", "additional_info")
MONGO_COLLECTION_NOTIFICATIONS = os.getenv("MONGO_COLLECTION_NOTIFICATIONS", "notifications")
USER_IMAGE_PATH = os.getenv("USER_IMAGE_PATH")
PATH_SONG = os.getenv("SONGS_PATH")
class Container(containers.DeclarativeContainer):
    mongo_db_provider = providers.Object(mongo_db)

    comments_collection = providers.Object(mongo_db[MONGO_COLLECTION_COMMENTS])
    additional_info_collection = providers.Object(mongo_db[MONGO_COLLECTION_ADDITIONAL_INFO])
    notifications_collection = providers.Object(mongo_db[MONGO_COLLECTION_NOTIFICATIONS])
    #Singletons
    user_image_manager = providers.Singleton(UserImageManager, base_dir=USER_IMAGE_PATH)
    song_file_manager = providers.Singleton(SognFileManager, base_dir=PATH_SONG)
    #Repositories
    song_extension_repository = providers.Factory(
        SongExtensionRepository,
        session=providers.Callable(SessionLocal)
    )
    song_repository = providers.Factory(
        SongRepository,
        session=providers.Callable(SessionLocal)
    )
    photo_repository = providers.Factory(
        PhotoRepository,
        session=providers.Callable(SessionLocal)
    )
    #Services
    user_image_service = providers.Factory(
        UserImageService,
        image_manager=user_image_manager,
        photo_repository=photo_repository
    )
    song_file_service = providers.Factory(
        SongService,
        song_manager = song_file_manager,
        song_repository = song_repository,
        song_extension_repository = song_extension_repository
    )
    #Controllers
    event_controller = providers.Factory(
        EventController
    )
    user_image_controller = providers.Factory(
        UserImageController,
        image_service=user_image_service
    )
    song_file_controller = providers.Factory(
        SongController,
        song_service=song_file_service
    )
