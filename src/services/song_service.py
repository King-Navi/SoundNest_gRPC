import os
import tempfile
import grpc
from typing import Iterator, Optional
from concurrent import futures

from streaming import song_pb2, song_pb2_grpc

class SongService(song_pb2_grpc.SongServiceServicer):
    """business-logic layer for all SongService RPCs."""

    def UploadSong(self, request: song_pb2.Song, context: grpc.ServicerContext) -> song_pb2.UploadSongResponse: #pylint: disable=E1101:no-member
        print("Hallelujah How'd you do it? (How'd you do it?)You been on my mind")
        #validate: `request.song_name`, `request.file`, `request.id_song_genre`, `request.description` with pydantic
        #save the file :(e.g. to disk or cloud storage)
        #persist metadata: in your database
        return song_pb2.UploadSongResponse(result=True, message="Uploaded successfully") #pylint: disable=E1101:no-member

    def UploadSongStream(
        self,
        request_iterator: Iterator[song_pb2.UploadSongRequest], # pylint: disable=E1101
        context: grpc.ServicerContext
    ) -> song_pb2.UploadSongResponse:  # pylint: disable=E1101
        metadata: Optional[song_pb2.UploadSongMetadata] = None # pylint: disable=E1101
        total_bytes: int = 0
        try:
            with tempfile.NamedTemporaryFile(suffix=".mp3", mode='w+b', delete=False) as temp_file_path:
                for request in request_iterator:
                    if request.HasField('metadata'):
                        metadata = request.metadata
                        print(f"[SERVER] Recibido metadata: {metadata.song_name}, género: {metadata.id_song_genre}")
                    elif request.HasField('chunk'):
                        chunk_data: bytes = request.chunk.chunk_data
                        temp_file_path.write(chunk_data)
                        total_bytes += len(chunk_data)
                        print(f"[SERVER] Recibido chunk de {len(chunk_data)} bytes")

            print(f"[SERVER] Canción completa recibida: {total_bytes} bytes en {temp_file_path}")
            # TODO: mover el archivo a destino final, guardar en DB, etc.
            #Puedes usar delete=True
            os.remove(temp_file_path.name)

            return song_pb2.UploadSongResponse(result=True, message="Stream uploaded successfully")  # pylint: disable=E1101

        except Exception as e:
            print(f"[SERVER] Error procesando el stream: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details('Error al procesar la canción')
            return song_pb2.UploadSongResponse(result=False, message="Error en el servidor")  # pylint: disable=E1101

    def DownloadSongStream(self, request: song_pb2.DownloadSongRequest, context: grpc.ServicerContext): #pylint: disable=E1101:no-member
        # TODO: look up song by request.id_song
        # TODO: yield a DownloadSongResponse(metadata=…) once at start
        # TODO: open file and for each chunk read and yield DownloadSongResponse(chunk=...)
        #     with file_handle as f:
        #         while chunk := f.read(64*1024):
        #             yield song_pb2.DownloadSongResponse(chunk=song_pb2.DownloadSongChunk(chunk_data=chunk))
        pass  # remove once implemented

    def DownloadSong(self, request: song_pb2.DownloadSongRequest, context: grpc.ServicerContext) -> song_pb2.DownloadSongData: #pylint: disable=E1101:no-member
        # TODO: look up song by request.id_song
        # TODO: read entire file into memory (only for small/medium files!)
        # data = open(...).read()
        # return song_pb2.DownloadSongData(
        #     song_name=…,
        #     file=data,
        #     id_song_genre=…,
        #     description=…
        # )
        pass  # remove once implemented
