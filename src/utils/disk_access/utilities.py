import io
import uuid
from PIL import Image
from services.errors.exceptions import InvalidImageContentError, InvalidImageFormatError, InvalidSongFormatError
from repository.photo_repository import PhotoRepository
from repository.song_repository import SongRepository


VALID_EXTENSIONS_IMAGES = {"png", "jpeg", "jpg"}

VALID_EXTENSIONS_SONGS = {"mp3", "wav"}

def is_valid_extension_song(extension: str):
    if not extension or extension.lower() not in VALID_EXTENSIONS_SONGS:
        raise InvalidSongFormatError(f"Invalid or missing file extension. Supported extensions: {VALID_EXTENSIONS_SONGS}")

def is_valid_extension_image(extension:str):
    if extension.lower() not in VALID_EXTENSIONS_IMAGES:
        raise InvalidImageFormatError(f"Unsupported image format. Supported extensions: {VALID_EXTENSIONS_IMAGES}")

def is_valid_image_file(image_bytes: bytes):
    try:
        with Image.open(io.BytesIO(image_bytes)) as img:
            img.verify()
    except Exception as e:
        raise InvalidImageContentError("Invalid image file.") from e

def generate_unique_resource_id_photo(photo_repository: PhotoRepository) -> str:
    while True:
        resource_id = str(uuid.uuid4())
        if not photo_repository.existe_filename(resource_id):
            return resource_id

def generate_unique_resource_id_song(song_repository: SongRepository) -> str:
    while True:
        resource_id = str(uuid.uuid4())
        if not song_repository.existe_filename(resource_id):
            return resource_id