#TODO: this go in controller
import uuid
import os
import grpc
from streaming import song_pb2
from services.storage import get_storage_path  # función que construye ruta en disco/S3

class SongService(song_pb2_grpc.SongServiceServicer):

    def UploadSongStream(self, request_iterator, context):
        # 1. Leer metadata
        try:
            first_msg = next(request_iterator)
        except StopIteration:
            context.abort(grpc.StatusCode.INVALID_ARGUMENT, "No messages received")
        
        if not first_msg.HasField("metadata"):
            context.abort(grpc.StatusCode.INVALID_ARGUMENT, "First message must be metadata")
        
        meta = first_msg.metadata
        if not meta.song_name:
            context.abort(grpc.StatusCode.INVALID_ARGUMENT, "song_name required")
        # ... validar id_song_genre, descripción, etc.

        # 2. Preparar storage
        song_id = str(uuid.uuid4())
        temp_path = get_storage_path(f"{song_id}.part")
        final_path = get_storage_path(f"{song_id}.mp3")
        os.makedirs(os.path.dirname(temp_path), exist_ok=True)

        try:
            with open(temp_path, "wb") as fh:
                # 3. Escribir chunks
                for msg in request_iterator:
                    if context.is_active() is False:
                        # Cliente canceló
                        fh.close()
                        os.remove(temp_path)
                        context.abort(grpc.StatusCode.CANCELLED, "Upload cancelled")
                    if not msg.HasField("chunk"):
                        continue
                    data = msg.chunk.chunk_data
                    # Límite de tamaño total (p. ej. 50 MB)
                    fh.write(data)
            # 4. Renombrar y persistir metadata
            os.rename(temp_path, final_path)
            # Aquí, guardar en DB: song_id, meta.song_name, meta.description, owner_id, ruta final_path
        except IOError as e:
            # Limpieza y respuesta de error
            if os.path.exists(temp_path):
                os.remove(temp_path)
            context.abort(grpc.StatusCode.INTERNAL, f"I/O error: {e}")

        return song_pb2.UploadSongResponse(
            result=True,
            message=f"Song uploaded with ID {song_id}"
        )
