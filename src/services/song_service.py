import uuid
import datetime
import logging
from typing import Iterator , Optional
from dependency_injector.wiring import inject
from generated.streaming.song_pb2 import  UploadSongMetadata #pylint: disable=E0611
from models.mysql.models import Song
from repository.song_repository import SongRepository
from repository.song_extension_repository import SongExtensionRepository
from repository.song_description_mongo_repository import SongDescriptionRepository
from utils.disk_access.utilities import generate_unique_resource_id_song, is_valid_extension_song
from utils.disk_access.song_file import SognFileManager
from utils.wrappers.song_wrapper import SongWithFile
from .errors.exceptions import MissingArguments, SongSavingError

VALID_EXTENSIONS = {"mp3"}
class SongService:
    """business-logic layer for all SongService RPCs."""
    @inject
    def __init__(self,
                song_manager: SognFileManager,
                song_repository : SongRepository,
                song_extension_repository : SongExtensionRepository,
                song_description_repository: SongDescriptionRepository
                ):
        self.song_manager :SognFileManager = song_manager
        self.song_repository :SongRepository = song_repository
        self.song_extension_repository : SongExtensionRepository = song_extension_repository
        self.song_description_repository : SongDescriptionRepository = song_description_repository
    async def handle_upload(
            self,
            user_id: int ,
            song_name : str,
            file_bytes : bytearray,
            extension : str,
            descripcion_song: str,
            id_song_genre: int )-> bool:
        is_valid_extension(extension)
        resource_id : str = generate_unique_resource_id_song(self.song_repository)
        await self.song_manager.save_song(file_bytes=file_bytes, extension=extension, file_name=resource_id)
        duration = await self.song_manager.get_audio_duration(resource_id, extension)

        new_song = Song(
            songName=song_name,
            fileName=resource_id,
            durationSeconds=round(duration),
            releaseDate=datetime.datetime.now(),
            isDeleted=False,
            idSongGenre=id_song_genre,
            idSongExtension= self.song_extension_repository.get_extension_id_by_name(extension),
            idAppUser=user_id
        )
        inserted_song = self.song_repository.insert_song( new_song )
        if not await self.song_manager.file_exists(resource_id,extension):
            self.song_repository.delete_song_by_filename(resource_id)
            raise SongSavingError("Failed to save image to disk.")
        await self.song_description_repository.add_description(author_id=user_id, song_id=inserted_song.idSong, text= descripcion_song)
        return True

    async def handle_upload_stream(self, request_iterator, user_id)-> bool:
        metadata : UploadSongMetadata = None
        total_bytes = 0
        file_bytes = bytearray()
        async for request in request_iterator:
            if request.HasField('metadata'):
                metadata = request.metadata
            elif request.HasField('chunk'):
                file_bytes.extend(request.chunk.chunk_data)
                total_bytes += len(request.chunk.chunk_data)
        check_arguments_upload_streaming(metadata, total_bytes)
        is_valid_extension_song(metadata.extension)

        resource_id : str = generate_unique_resource_id_song(self.song_repository)
        await self.song_manager.save_song(file_bytes=file_bytes, extension=metadata.extension, file_name=resource_id)
        duration = await self.song_manager.get_audio_duration(resource_id, metadata.extension)

        new_song = Song(
            songName=metadata.song_name,
            fileName=resource_id,
            durationSeconds=round(duration),
            releaseDate=datetime.datetime.now(),
            isDeleted=False,
            idSongGenre=metadata.id_song_genre,
            idSongExtension= self.song_extension_repository.get_extension_id_by_name(metadata.extension),
            idAppUser=user_id
        )
        inserted_song = self.song_repository.insert_song( new_song )

        if not await self.song_manager.file_exists(resource_id, metadata.extension):
            self.song_repository.delete_song_by_filename(resource_id)
            raise SongSavingError("Failed to save image to disk.")
        await self.song_description_repository.add_description(author_id=user_id, song_id=inserted_song.idSong, text= metadata.description)
        return True

    async def handle_download(self, song_id: int) -> tuple[SongWithFile, str, str]:
        song: Song = self.song_repository.get_song_by_id(song_id)
        if song is None:
            raise ValueError("Song not found")

        extension = self.song_extension_repository.get_extension_name_by_id(song.idSongExtension) or "unknown"
        file_bytes: bytes = await self.song_manager.load_song_file(song.fileName, extension)

        description = await self.song_description_repository.get_description_by_song_id(song.idSong)

        song_wrapper = SongWithFile(song=song, file_content=file_bytes)
        return song_wrapper, description, extension
    
    async def handle_download_stream(self, song_id: int) -> tuple[Song, Iterator[bytes], Optional[str]]:
        song: Song = self.song_repository.get_song_by_id(song_id)
        if song is None:
            raise ValueError("Song not found")
        extension = self.song_extension_repository.get_extension_name_by_id(song.idSongExtension)
        logging.info(extension)
        if not extension:
            raise ValueError(f"Extension not found for song ID {song_id}")
        extension = extension.strip().lower()
        if extension not in {"mp3"}:
            raise ValueError(f"Unsupported extension '{extension}' for song ID {song_id}")
        chunk_generator = self.song_manager.read_resource_stream((song.fileName, extension))
        description = await self.song_description_repository.get_description_by_song_id(song.idSong)
        return song, chunk_generator, description

    def _generate_unique_resource_id(self) -> str:
        while True:
            resource_id = str(uuid.uuid4())
            if not self.song_repository.existe_filename(resource_id):
                return resource_id

def check_arguments_upload_streaming(metadata , total_bytes):
    if metadata is None:
        raise MissingArguments("metadata")
    if total_bytes <= 0:
        raise MissingArguments("chunk")
    is_valid_extension(metadata.extension)

def is_valid_extension(extension :str):
    if not extension or extension.lower() not in VALID_EXTENSIONS:
        raise ValueError(f"Invalid or missing file extension. Supported extensions: {VALID_EXTENSIONS}")
