import os
from dependency_injector import containers, providers
from sqlalchemy.orm import sessionmaker
from repository.photo_repository import PhotoRepository
from controller.user_controller import UserImageController
from services.user_images_service import UserImageService
from utils.disk_access.user_image import UserImageManager

from config.connection_mysql import SessionLocal
from config.connection_mongo import db as mongo_db

from dotenv import load_dotenv
load_dotenv()
MONGO_COLLECTION_COMMENTS = os.getenv("MONGO_COLLECTION_COMMENTS", "comments")
MONGO_COLLECTION_ADDITIONAL_INFO = os.getenv("MONGO_COLLECTION_ADDITIONAL_INFO", "additional_info")
MONGO_COLLECTION_NOTIFICATIONS = os.getenv("MONGO_COLLECTION_NOTIFICATIONS", "notifications")

class Container(containers.DeclarativeContainer):
    mongo_db_provider = providers.Object(mongo_db)

    comments_collection = providers.Object(mongo_db[MONGO_COLLECTION_COMMENTS])
    additional_info_collection = providers.Object(mongo_db[MONGO_COLLECTION_ADDITIONAL_INFO])
    notifications_collection = providers.Object(mongo_db[MONGO_COLLECTION_NOTIFICATIONS])
    
    user_image_manager = providers.Singleton(UserImageManager)
    photo_repository = providers.Factory(
        PhotoRepository,
        session=providers.Callable(SessionLocal)
    )
    user_image_service = providers.Factory(
        UserImageService,
        image_manager=user_image_manager,
        photo_repository=photo_repository
    )
