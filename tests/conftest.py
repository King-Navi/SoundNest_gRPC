import sys
import types
from unittest.mock import MagicMock

# modulo user_photo para evitar errores por archivos gRPC mal generados
fake_user_photo = types.ModuleType("user_photo")
fake_user_photo.user_image_pb2 = MagicMock()
fake_user_photo.user_image_pb2_grpc = MagicMock()
fake_user_photo.user_image_pb2_grpc.UserImageServiceServicer = object

sys.modules["user_photo"] = fake_user_photo

import pytest
from unittest.mock import AsyncMock, MagicMock
from dependency_injector import containers, providers
from dependency_injector.wiring import Provide
from src.utils.rest_api import app
from src.repository.song_repository import SongRepository
from src.utils.disk_access.song_file import SognFileManager


class TestContainer(containers.DeclarativeContainer):
    song_repository = providers.Object(MagicMock(spec=SongRepository))
    song_file_manager = providers.Object(AsyncMock(spec=SognFileManager))

test_container = TestContainer()

@pytest.fixture(autouse=True)
def override_dependencies():
    app.dependency_overrides[Provide["Container.song_repository"]] = lambda: test_container.song_repository()
    app.dependency_overrides[Provide["Container.song_file_manager"]] = lambda: test_container.song_file_manager()
    return test_container
