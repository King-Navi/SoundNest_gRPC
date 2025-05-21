from dependency_injector import containers, providers

from utils.injection.base_conteiner import BaseContainer
from controller.event_controller import EventController
from controller.user_controller import UserImageController
from controller.song_controller import SongController
from controller.utils.client_registry import ClientRegistry
from services.user_images_service import UserImageService
from services.song_service import SongService
from services.event_service import EventService 
class Container(BaseContainer):
    client_registry = providers.Singleton(
        ClientRegistry
    )

    #Services
    user_image_service = providers.Factory(
        UserImageService,
        image_manager=BaseContainer.user_image_manager,
        photo_repository=BaseContainer.photo_repository
    )
    song_file_service = providers.Factory(
        SongService,
        song_manager = BaseContainer.song_file_manager,
        song_repository = BaseContainer.song_repository,
        song_extension_repository = BaseContainer.song_extension_repository
    )
    event_service = providers.Factory(
        EventService
    )
    #Controllers
    event_controller = providers.Factory(
        EventController,
        event_service=event_service,
        client_registry=client_registry,
        client_msg_android=BaseContainer.client_msg_android

    )
    user_image_controller = providers.Factory(
        UserImageController,
        image_service=user_image_service
    )
    song_file_controller = providers.Factory(
        SongController,
        song_service=song_file_service
    )
