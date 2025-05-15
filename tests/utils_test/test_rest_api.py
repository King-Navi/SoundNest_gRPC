import pytest
from httpx import AsyncClient
from src.utils.rest_api import app
from models.mysql.models import Song, SongExtension

@pytest.mark.asyncio
async def test_delete_song_success(override_dependencies):
    mock_repo = override_dependencies.song_repository()
    mock_file_manager = override_dependencies.song_file_manager()
    mock_song = Song()
    mock_song.fileName = "testfile"
    mock_song.SongExtension_ = SongExtension(extensionName="mp3")
    mock_repo.get_song_by_id.return_value = mock_song
    mock_repo.delete_song.return_value = True
    mock_file_manager.delete_file.return_value = True

    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.delete("/delete/song/123")

    assert response.status_code == 200
    assert response.json() == {"message": "Song 123 deleted successfully"}
    mock_repo.get_song_by_id.assert_called_once_with(123)
    mock_file_manager.delete_file.assert_awaited_once_with("testfile", "mp3")
    mock_repo.delete_song.assert_called_once_with(123)