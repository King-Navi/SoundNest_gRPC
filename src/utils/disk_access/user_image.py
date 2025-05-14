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
        resource_id_value, extension = resource_id
        filename = f"{resource_id_value}.{extension.lstrip('.')}"
        return self.base_dir / filename

    async def save_user_image(self, resource_id, image_bytes, extension="png"):
        await self.write_resource((resource_id, extension), image_bytes)

    async def load_user_image(self, resource_id, extension="png")-> bytes:
        return await self.read_resource((resource_id, extension))
    
    async def file_exists(self, resource_id: str, extension: str) -> bool:
        path = self._get_file_path((resource_id, extension))
        return await asyncio.to_thread(path.exists)
