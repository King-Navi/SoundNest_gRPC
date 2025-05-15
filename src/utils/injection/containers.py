from dependency_injector import containers, providers

from utils.injection.base_conteiner import BaseContainer
from controller.event_controller import EventController
from controller.user_controller import UserImageController
from controller.song_controller import SongController
from services.user_images_service import UserImageService
from services.song_service import SongService

class Container(BaseContainer):
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
