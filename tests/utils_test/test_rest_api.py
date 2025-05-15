import pytest
from httpx import AsyncClient , ASGITransport
from unittest.mock import AsyncMock , MagicMock
from models.mysql.models import Song, SongExtension
from src.utils.rest_api import app
from src.repository.song_repository import SongRepository
from src.utils.disk_access.song_file import SognFileManager
from src.utils.rest_api import get_song_repository, get_file_manager

@pytest.mark.asyncio
async def test_delete_song_success():
    mock_repo = MagicMock(spec=SongRepository)
    mock_file_manager = AsyncMock(spec=SognFileManager)
    
    mock_song = Song()
    mock_song.fileName = "testfile"
    mock_song.SongExtension_ = SongExtension(extensionName="mp3")
    mock_repo.get_song_by_id.return_value = mock_song
    mock_repo.delete_song.return_value = True
    mock_file_manager.delete_file.return_value = True
    
    app.dependency_overrides[get_song_repository] = lambda: mock_repo
    app.dependency_overrides[get_file_manager] = lambda: mock_file_manager
    
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.delete("/delete/song/123")

    assert response.status_code == 200
    assert response.json() == {"message": "Song 123 deleted successfully"}
    mock_repo.get_song_by_id.assert_called_once_with(123)
    mock_file_manager.delete_file.assert_awaited_once_with("testfile", "mp3")
    mock_repo.delete_song.assert_called_once_with(123)