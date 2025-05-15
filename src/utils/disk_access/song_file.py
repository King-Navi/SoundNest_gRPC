import asyncio
from pathlib import Path
from tinytag import TinyTag
from typing_extensions import override
import aiofiles
from .base_resource_manager import BaseResourceManager
DEFAULT_CHUNK_SIZE = 64 * 1024  # 64 KB
class SognFileManager(BaseResourceManager):
    @override
    def _get_file_path(self, resource_id):
        resource_id_value, extension = resource_id
        filename = f"{resource_id_value}.{extension.lstrip('.')}"
        return self.base_dir / filename

    async def save_song(self, file_bytes, extension, file_name) -> Path:
        self._validate_file_content(file_bytes, extension)
        self.base_dir.mkdir(parents=True, exist_ok=True)
        await self.write_resource((file_name, extension), file_bytes)
        return self._get_file_path((file_name, extension))

    def _validate_file_content(self,file_bytes: bytes, extension: str):
        if extension.lower() == "mp3":
            if not (file_bytes.startswith(b"ID3") or file_bytes[0:2] == b'\xff\xfb'):
                raise ValueError("Invalid MP3 file content.")
        elif extension.lower() == "wav":
            if not (file_bytes.startswith(b"RIFF") and file_bytes[8:12] == b"WAVE"):
                raise ValueError("Invalid WAV file content.")
        else:
            raise ValueError("Unsupported file extension for content validation.")

    async def file_exists(self, resource_id: str, extension: str) -> bool:
        path = self._get_file_path((resource_id, extension))
        return await asyncio.to_thread(path.exists)

    def get_audio_duration(self, resource_id: str, extension: str) -> float:
        file_path = self._get_file_path((resource_id, extension))
        if not file_path.exists():
            raise FileNotFoundError(f"File {file_path} does not exist.")
        tag = TinyTag.get(str(file_path))
        return tag.duration

    async def load_song_file(self, resource_id: str, extension: str = "mp3")-> bytes:
        return await self.read_resource((resource_id, extension))

    async def read_resource_stream(self, resource_id: tuple, chunk_size: int = DEFAULT_CHUNK_SIZE):
        """Async generator that yields file content in chunks."""
        resource_key = self._get_resource_key(resource_id)
        lock = await self._get_lock(resource_key)
        mode = "rb"

        async with lock:
            try:
                path = self._get_file_path(resource_id)
                async with aiofiles.open(path, mode) as f:
                    while True:
                        chunk = await f.read(chunk_size)
                        if not chunk:
                            break
                        yield chunk
            except (IOError, OSError) as e:
                raise e

    async def delete_file(self, resource_id: str, extension: str) -> bool:
        resource_key = self._get_resource_key((resource_id, extension))
        lock = await self._get_lock(resource_key)
        async with lock:
            path = self._get_file_path((resource_id, extension))
            if await asyncio.to_thread(path.exists):
                await asyncio.to_thread(path.unlink)
                return True
            return False
