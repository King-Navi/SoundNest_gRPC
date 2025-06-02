import pytest
from unittest.mock import AsyncMock, MagicMock
from dependency_injector.wiring import Provide
from dependency_injector import providers
from src.utils.injection.base_conteiner import BaseContainer
from src.repository.song_repository import SongRepository
from src.utils.disk_access.song_file import SognFileManager

@pytest.fixture(autouse=True)
def override_dependencies():
    """Override de dependencias reales por mocks para pruebas unitarias"""
    mock_song_repo = MagicMock(spec=SongRepository)
    mock_file_manager = AsyncMock(spec=SognFileManager)

    # Reemplaza proveedores directamente
    container = BaseContainer()
    container.song_repository.override(mock_song_repo)
    container.song_file_manager.override(mock_file_manager)


    return {
        "song_repository": mock_song_repo,
        "song_file_manager": mock_file_manager
    }