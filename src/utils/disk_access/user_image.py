import os
import asyncio
from dotenv import load_dotenv
from typing_extensions import override

from .base_resource_manager import BaseResourceManager

load_dotenv()

user_image_path = os.getenv("USER_IMAGE_PATH")

class UserImageManager(BaseResourceManager):

    @override
    def _get_file_path(self, resource_id):
        """
        Constructs the file path for a given resource ID and extension.

        Args:
            resource_id (tuple): A tuple of (resource_id: str, extension: str)

        Returns:
            pathlib.Path: The full path to the resource file.
        """
        resource_id_value, extension = resource_id
        filename = f"{resource_id_value}.{extension.lstrip('.')}"
        return self.base_dir / filename

    async def save_user_image(self, resource_id, image_bytes, extension="png"):
        """
        Saves a user's image asynchronously.

        Args:
            resource_id (str): Unique identifier for the user/image.
            image_bytes (bytes): Binary content of the image.
            extension (str, optional): Image file extension. Defaults to "png".
        """
        await self.write_resource((resource_id, extension), image_bytes)

    async def load_user_image(self, resource_id, extension="png")-> bytes:
        """
        Loads a user's image asynchronously.

        Args:
            resource_id (str): Unique identifier for the user/image.
            extension (str, optional): Image file extension. Defaults to "png".

        Returns:
            bytes: The binary content of the image.
        """ 
        return await self.read_resource((resource_id, extension))
    
    async def file_exists(self, resource_id: str, extension: str) -> bool:
        """
        Checks whether a user's image file exists.

        Args:
            resource_id (str): Unique identifier for the user/image.
            extension (str): Image file extension.

        Returns:
            bool: True if the file exists, False otherwise.
        """
        path = self._get_file_path((resource_id, extension))
        return await asyncio.to_thread(path.exists)
