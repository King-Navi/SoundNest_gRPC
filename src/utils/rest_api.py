from fastapi import FastAPI, HTTPException, Depends
from utils.injection.base_conteiner import BaseContainer
from utils.disk_access.song_file import SognFileManager
from repository.song_repository import SongRepository
app = FastAPI()

def get_file_manager() -> SognFileManager:
    return BaseContainer.song_file_manager()

def get_song_repository() -> SongRepository:
    return BaseContainer.song_repository()


@app.delete("/delete/song/{idsong}")
async def delete_song_file(
    idsong: int,
    file_manager: SognFileManager = Depends(get_file_manager),
    song_repo: SongRepository = Depends(get_song_repository)
):
    if idsong <= 0:
        raise HTTPException(status_code=400, detail="Invalid song ID")
    song = song_repo.get_song_by_id(idsong)
    if not song:
        raise HTTPException(status_code=404, detail="Song not found in database")
        
    filename = song.fileName
    extension = song.SongExtension_.extensionName if song.SongExtension_ else None
    if not filename or not extension:
        raise HTTPException(status_code=500, detail="Incomplete song metadata")
    try:
        deleted = await file_manager.delete_file(filename, extension)
        if not deleted:
            raise HTTPException(status_code=404, detail="File not found on disk")
        success = song_repo.delete_song(idsong)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to delete song from database")

        return {"message": f"Song {idsong} deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) #pylint: disable=W0707