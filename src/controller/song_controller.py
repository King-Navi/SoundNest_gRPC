import logging
from typing import Iterator, Optional
import grpc
from grpc.aio import ServicerContext

from dependency_injector.wiring import Provider, inject
from streaming import song_pb2, song_pb2_grpc

from services.song_service import SongService
from utils.wrappers.song_wrapper import SongWithFile , Song

from interceptors.jwt_interceptor import _JWT_PAYLOAD

class SongController(song_pb2_grpc.SongServiceServicer):
    @inject
    def __init__(self, song_service: SongService = Provider["song_service"]):
        self.song_service = song_service

    async def UploadSong(self, request: song_pb2.Song, context: ServicerContext) -> song_pb2.UploadSongResponse: #pylint: disable=E1101:no-member
        jwt_payload = _JWT_PAYLOAD.get(None)
        if not jwt_payload:
            await context.abort(grpc.StatusCode.UNAUTHENTICATED, "Missing authentication token")
        user_id = jwt_payload.get('id')
        username = jwt_payload.get('username')
        role_id = jwt_payload.get('role')
        email = jwt_payload.get('email')
        try:
            result = await self.song_service.handle_upload(
                user_id=user_id,
                song_name=request.song_name,
                file_bytes=request.file,
                extension=request.extension,
                descripcion_song=request.description,
                id_song_genre=request.id_song_genre
            )
            return song_pb2.UploadSongResponse( # pylint: disable=E1101
                result=True,
                message="Song uploaded"
            )
        except Exception as e:
            return song_pb2.UploadSongResponse( # pylint: disable=E1101
                result=False,
                message=f"Failed to upload Song: {str(e)}"
            )
        
    async def UploadSongStream(self,  request_iterator: Iterator[song_pb2.UploadSongRequest], context: ServicerContext)-> song_pb2.UploadSongResponse: # pylint: disable=E1101
        jwt_payload = _JWT_PAYLOAD.get(None)
        if not jwt_payload:
            await context.abort(grpc.StatusCode.UNAUTHENTICATED, "Missing authentication token")

        user_id = jwt_payload.get('id')
        username = jwt_payload.get('username')
        role_id = jwt_payload.get('role')
        email = jwt_payload.get('email')
        logging.debug(f"Authenticated user: {username} ({user_id})")
        try:
            result = await self.song_service.handle_upload_stream(request_iterator, user_id)
            return song_pb2.UploadSongResponse( # pylint: disable=E1101
                result=True,
                message="Song uploaded"
            )
        except Exception as e:
            return song_pb2.UploadSongResponse( # pylint: disable=E1101
                result=False,
                message=f"Failed to upload Song: {str(e)}"
            )

    async def DownloadSongStream(self, request: song_pb2.DownloadSongRequest, context: ServicerContext)-> Iterator[song_pb2.DownloadSongResponse] : #pylint: disable=E1101:no-member
        try:
            song_entity, chunk_generator = await self.song_service.handle_download_stream(request.id_song)
            
            # send metadata
            yield song_pb2.DownloadSongResponse( # pylint: disable=E1101
                metadata=song_pb2.DownloadSongMetadata( # pylint: disable=E1101
                    song_name=song_entity.fileName,
                    id_song_genre=song_entity.idSongGenre,
                    description="song_entity.description", #TODO:
                    extension="song_entity.extension" #TODO:
                )
            )

            # send chunks
            async for chunk in chunk_generator:
                yield song_pb2.DownloadSongResponse( # pylint: disable=E1101
                    chunk=song_pb2.DownloadSongChunk(chunk_data=chunk) # pylint: disable=E1101
                )

        except Exception as e:
            await context.abort(grpc.StatusCode.NOT_FOUND, f"Song not found or failed: {str(e)}")

    async def DownloadSong(self, request: song_pb2.DownloadSongRequest, context: ServicerContext) -> song_pb2.DownloadSongData: #pylint: disable=E1101:no-member
        try:
            result : SongWithFile = await self.song_service.handle_download(request.id_song)

            return song_pb2.DownloadSongData( # pylint: disable=E1101
                song_name= result.song.fileName,
                file=result.file_content,
                id_song_genre=result.song.idSongGenre,
                description="#TODO: Ivan no ha hecho esto porque se canso", #TODO: Ivan no ha hecho esto porque se canso
                extension="result.song.idSongExtension"
            )
        except Exception as e:
            await context.abort(grpc.StatusCode.NOT_FOUND, f"Song not found: {str(e)}")
