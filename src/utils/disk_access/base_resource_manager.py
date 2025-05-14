import os
from pathlib import Path
import asyncio
import aiofiles

class BaseResourceManager:
    def __init__(self, base_dir):
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self.locks : dict = {}
        self.locks_lock = asyncio.Lock()

    async def _get_lock(self, resource_key: tuple) -> asyncio.Lock:
        async with self.locks_lock:
            if resource_key not in self.locks:
                self.locks[resource_key] = asyncio.Lock()
            return self.locks[resource_key]

    def _get_resource_key(self, resource_id: tuple) -> tuple:
        return resource_id

    def _get_file_path(self, resource_id: tuple) -> Path:
        raise NotImplementedError("Subclasses must implement _get_file_path")

    async def read_resource(self, resource_id: tuple, binary=True)-> bytes|str:
        resource_key = self._get_resource_key(resource_id)
        lock = await self._get_lock(resource_key)
        mode = "rb" if binary else "r"

        async with lock:
            try:
                path = self._get_file_path(resource_id)
                async with aiofiles.open(path, mode) as f:
                    return await f.read()
            except IOError as e:
                raise e

    async def write_resource(self, resource_id: tuple, data, binary=True):
        resource_key = self._get_resource_key(resource_id)
        lock = await self._get_lock(resource_key)
        mode = "wb" if binary else "w"

        async with lock:
            try:
                path = self._get_file_path(resource_id)
                os.makedirs(path.parent, exist_ok=True)
                async with aiofiles.open(path, mode) as f:
                    await f.write(data)
            except IOError as e:
                raise e