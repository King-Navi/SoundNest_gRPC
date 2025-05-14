import uuid
import datetime
import logging
from typing import Iterator
from dependency_injector.wiring import inject
from generated.streaming.song_pb2 import  UploadSongMetadata #pylint: disable=E0611
from models.mysql.models import Song
from repository.song_repository import SongRepository
from repository.song_extension_repository import SongExtensionRepository
from utils.disk_access.utilities import generate_unique_resource_id_song, is_valid_extension_song
from utils.disk_access.song_file import SognFileManager
from utils.wrappers.song_wrapper import SongWithFile
from .errors.exceptions import MissingArguments, SongSavingError

VALID_EXTENSIONS = {"mp3", "wav"}
class SongService:
    """business-logic layer for all SongService RPCs."""
    @inject
    def __init__(self,
                song_manager: SognFileManager,
                song_repository : SongRepository,
                song_extension_repository : SongExtensionRepository
                ):
        self.song_manager :SognFileManager = song_manager
        self.song_repository :SongRepository = song_repository
        self.song_extension_repository : SongExtensionRepository = song_extension_repository
    def handle_upload(
            self,user_id: int ,
            song_name : str,
            file_bytes : bytearray,
            extension : str,
            descripcion_song: str,
            id_song_genre: int )-> bool:
        is_valid_extension(extension)
        resource_id : str = generate_unique_resource_id_song(self.song_repository)
        self.song_manager.save_song(file_bytes=file_bytes, extension=extension, file_name=resource_id)

        new_song = Song(
            songName=song_name,
            fileName=resource_id,
            durationSeconds=round(self.song_manager.get_audio_duration(resource_id, extension)),
            releaseDate=datetime.datetime.now(),
            isDeleted=False,
            idSongGenre=id_song_genre,
            idSongExtension= self.song_extension_repository.get_extension_id_by_name(extension),
            idAppUser=user_id
        )
        self.song_repository.insert_song( new_song )
        if not self.song_manager.file_exists(resource_id,extension):
            self.song_repository.delete_song_by_filename(resource_id)
            raise SongSavingError("Failed to save image to disk.")
        #TODO: Put in mongo the Metada descripcion
        return True

    def handle_upload_stream(self, request_iterator, user_id)-> bool:
        metadata : UploadSongMetadata = None
        total_bytes = 0
        chunks = []
        for request in request_iterator:
            if request.HasField('metadata'):
                metadata = request.metadata
            elif request.HasField('chunk'):
                chunks.append(request.chunk.chunk_data)
                total_bytes += len(request.chunk.chunk_data)
        check_arguments_upload_streaming(metadata, total_bytes)
        file_bytes = b''.join(chunks)
        is_valid_extension_song(metadata.extension)

        resource_id : str = generate_unique_resource_id_song(self.song_repository)
        self.song_manager.save_song(file_bytes=file_bytes, extension=metadata.extension, file_name=resource_id)
        new_song = Song(
            songName=metadata.song_name,
            fileName=resource_id,
            durationSeconds=round(self.song_manager.get_audio_duration(resource_id, metadata.extension)),
            releaseDate=datetime.datetime.now(),
            isDeleted=False,
            idSongGenre=metadata.id_song_genre,
            idSongExtension= self.song_extension_repository.get_extension_id_by_name(metadata.extension),
            idAppUser=user_id
        )
        self.song_repository.insert_song( new_song )

        if not self.song_manager.file_exists(resource_id, metadata.extension):
            self.song_repository.delete_song_by_filename(resource_id)
            raise SongSavingError("Failed to save image to disk.")
        #TODO: Put in mongo the Metada descripcion
        return True

    def handle_download(self, song_id : int) -> Song:
        #TODO: CADA VEZ SE TIENE QUE AUMENTAR LA VISAULIZACION SI NO ES AQUI ES EN RESTFUL
        logging.debug(f"[song_service.py] song_id recibido: {song_id}")
        song: Song = self.song_repository.get_song_by_id(song_id)
        if song is None:
            raise ValueError("Song not found")
        file_bytes: bytes = self.song_manager.load_song_file(song.fileName, self.song_extension_repository.get_extension_name_by_id(song.idSongExtension))
        song_wrapper = SongWithFile(song=song, file_content=file_bytes)
        return song_wrapper
    
    def handle_download_stream(self, song_id: int) -> tuple[Song, Iterator[bytes]]:
        #TODO: CADA VEZ SE TIENE QUE AUMENTAR LA VISAULIZACION SI NO ES AQUI ES EN RESTFUL
        logging.debug(f"[song_service.py] song_id recibido: {song_id}")
        song: Song = self.song_repository.get_song_by_id(song_id)
        if song is None:
            raise ValueError("Song not found")
        chunk_generator = self.song_manager.read_resource_stream((song.fileName, self.song_extension_repository.get_extension_name_by_id(song.idSongExtension)))
        return song, chunk_generator

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
