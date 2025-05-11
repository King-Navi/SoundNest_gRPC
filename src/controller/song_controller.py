import logging
from typing import Iterator, Optional
import grpc
from dependency_injector.wiring import Provider, inject
from streaming import song_pb2, song_pb2_grpc

from services.song_service import SongService
from utils.wrappers.song_wrapper import SongWithFile , Song


class SongController(song_pb2_grpc.SongServiceServicer):
    @inject
    def __init__(self, song_service: SongService = Provider["song_service"]):
        self.song_service = song_service

    def UploadSong(self, request: song_pb2.Song, context: grpc.ServicerContext) -> song_pb2.UploadSongResponse: #pylint: disable=E1101:no-member
        jwt_payload = getattr(context, 'jwt_payload', None)
        if not jwt_payload:
            context.abort(grpc.StatusCode.UNAUTHENTICATED, "Missing authentication token")

        user_id = jwt_payload.get('id')
        username = jwt_payload.get('username')
        role_id = jwt_payload.get('role')
        email = jwt_payload.get('email')
        try:
            result = self.song_service.handle_upload(
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
                success=False,
                message=f"Failed to upload Song: {str(e)}"
            )
        
    def UploadSongStream(self,  request_iterator: Iterator[song_pb2.UploadSongRequest], context: grpc.ServicerContext)-> song_pb2.UploadSongResponse: # pylint: disable=E1101
        jwt_payload = getattr(context, 'jwt_payload', None)
        if not jwt_payload:
            context.abort(grpc.StatusCode.UNAUTHENTICATED, "Missing authentication token")

        user_id = jwt_payload.get('id')
        username = jwt_payload.get('username')
        role_id = jwt_payload.get('role')
        email = jwt_payload.get('email')
        logging.debug(f"Authenticated user: {username} ({user_id})")
        try:
            result = self.song_service.handle_upload_stream(request_iterator, user_id)
            return song_pb2.UploadSongResponse( # pylint: disable=E1101
                result=True,
                message="Song uploaded"
            )
        except Exception as e:
            return song_pb2.UploadSongResponse( # pylint: disable=E1101
                success=False,
                message=f"Failed to upload Song: {str(e)}"
            )

    def DownloadSongStream(self, request: song_pb2.DownloadSongRequest, context: grpc.ServicerContext)-> Iterator[song_pb2.DownloadSongResponse] : #pylint: disable=E1101:no-member
        try:
            song_entity, chunk_generator = self.song_service.handle_download_stream(request.id_song)
            
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
            for chunk in chunk_generator:
                yield song_pb2.DownloadSongResponse( # pylint: disable=E1101
                    chunk=song_pb2.DownloadSongChunk(chunk_data=chunk) # pylint: disable=E1101
                )

        except Exception as e:
            context.abort(grpc.StatusCode.NOT_FOUND, f"Song not found or failed: {str(e)}")

    def DownloadSong(self, request: song_pb2.DownloadSongRequest, context: grpc.ServicerContext) -> song_pb2.DownloadSongData: #pylint: disable=E1101:no-member
        try:
            logging.debug(f"Tipo de request: {type(request)}")
            logging.debug(f"Contenido recibido: {request}")
            logging.debug(f"[DownloadSong] request.ListFields: {request.ListFields()}")
            result : SongWithFile = self.song_service.handle_download(request.id_song)

            return song_pb2.DownloadSongData( # pylint: disable=E1101
                song_name= result.song.fileName,
                file=result.file_content,
                id_song_genre=result.song.idSongGenre,
                description="#TODO: Ivan no ha hecho esto porque se canso", #TODO: Ivan no ha hecho esto porque se canso
                extension="result.song.idSongExtension"
            )
        except Exception as e:
            context.abort(grpc.StatusCode.NOT_FOUND, f"Song not found: {str(e)}")
