import os
from pathlib import Path
from tinytag import TinyTag
from typing_extensions import override
from .base_resource_manager import BaseResourceManager

DEFAULT_CHUNK_SIZE = 64 * 1024  # 64 KB
class SognFileManager(BaseResourceManager):
    @override
    def _get_file_path(self, resource_id):
        resource_id_value, extension = resource_id
        filename = f"{resource_id_value}.{extension.lstrip('.')}"
        return self.base_dir / filename

    def save_song(self, file_bytes, extension, file_name) -> Path:
        self._validate_file_content(file_bytes, extension)
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self.write_resource((file_name, extension), file_bytes)
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

    def file_exists(self, resource_id: str, extension: str) -> bool:
        return self._get_file_path((resource_id, extension)).exists()

    def get_audio_duration(self, resource_id: str, extension: str) -> float:
        file_path = self._get_file_path((resource_id, extension))
        if not file_path.exists():
            raise FileNotFoundError(f"File {file_path} does not exist.")
        tag = TinyTag.get(str(file_path))
        return tag.duration
    
    def load_song_file(self, resource_id, extension="mp3")-> bytes:
        return self.read_resource((resource_id, extension))
    
    def read_resource_stream(self, resource_id: tuple, chunk_size: int = DEFAULT_CHUNK_SIZE):
        """Generator that yields file content in chunks."""
        resource_key = self._get_resource_key(resource_id)
        lock = self._get_lock(resource_key)
        mode = "rb"

        with lock:
            try:
                path = self._get_file_path(resource_id)
                with open(path, mode) as f:
                    while True:
                        chunk = f.read(chunk_size)
                        if not chunk:
                            break
                        yield chunk
            except IOError as e:
                raise e
