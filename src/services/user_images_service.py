from datetime import datetime
from dependency_injector.wiring import inject
from models.mysql.models import Photo
from utils.disk_access.utilities import (
    is_valid_extension_image,
    is_valid_image_file,
    generate_unique_resource_id_photo
)
from utils.disk_access.user_image import UserImageManager
from repository.photo_repository import PhotoRepository
from .errors.exceptions import ImageSavingError

class UserImageService:
    @inject
    def __init__(self,
                image_manager: UserImageManager,
                photo_repository : PhotoRepository
                ):
        self.image_manager = image_manager
        self.photo_repository = photo_repository

    async def upload_image(self,id_user:int, image_bytes:bytes, extension:str):
        """
        Uploads a user image.
        :param id_user: User identifier
        :param resource_id: Unique resource identifier
        :param image_bytes: Binary content of the image
        :param extension: File extension (png, jpeg, jpg)

        :raises InvalidImageFormatError: If the extension is not supported
        :raises InvalidImageContentError: If the file is not a valid image
        :raises ImageSavingError: If the image could not be saved

        :see: is_valid_extension
        :see: is_valid_image_file
        """
        is_valid_extension_image(extension)
        is_valid_image_file(image_bytes)
        if self.photo_repository.has_image(id_user):
            photos: list[Photo] = self.photo_repository.get_photos_by_user_id(id_user)
            if not photos:
                raise RuntimeError("Inconsistent state: has_image=True but no photos returned.")
            await self.image_manager.save_user_image(photos[0].fileName, image_bytes, extension)
            if not await self.image_manager.file_exists(photos[0].fileName, extension):
                self.photo_repository.delete_photo(photos[0].idPhoto)
                raise ImageSavingError("Failed to save image to disk.")
            self.photo_repository.update_photo(photos[0].idPhoto, extension=extension,createdAt= datetime.now())

        else:
            resource_id = generate_unique_resource_id_photo(self.photo_repository)
            photo = self.photo_repository.add_photo(file_name=resource_id,extension= extension,id_user=id_user )
            await self.image_manager.save_user_image(resource_id, image_bytes, extension)
            if not await self.image_manager.file_exists(resource_id, extension):
                self.photo_repository.delete_photo(photo.idPhoto)
                raise ImageSavingError("Failed to save image to disk.")

    async def download_image(self, resource_id: str, extension: str) -> bytes:
        return await self.image_manager.load_user_image(resource_id, extension)
