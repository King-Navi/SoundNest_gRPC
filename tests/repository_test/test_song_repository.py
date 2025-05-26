import pytest
from datetime import datetime
from models.mysql.models import Song
from repository.song_repository import SongRepository

from src.config.connection_mysql import engine , SessionLocal


@pytest.fixture
def db_session():
    connection = engine.connect()
    transaction = connection.begin()
    session = SessionLocal(bind=connection)
    yield session
    session.close()
    transaction.rollback()
    connection.close()

def create_song():
    return Song(
        songName="Prueba",
        fileName="archivo_unico_123",
        durationSeconds=120,
        releaseDate=datetime.now(),
        idSongGenre=1,
        idSongExtension=1,
        idAppUser=1
    )

def test_insert_and_get_song_by_id(db_session):
    repo = SongRepository(db_session)
    song = create_song()
    assert repo.insert_song(song) is not None
    assert song.idSong is not None
    fetched = repo.get_song_by_id(song.idSong)
    assert fetched is not None
    assert fetched.fileName == "archivo_unico_123"

def test_existe_filename_true(db_session):
    repo = SongRepository(db_session)
    song = create_song()
    repo.insert_song(song)
    assert repo.existe_filename("archivo_unico_123") is True

def test_existe_filename_false(db_session):
    repo = SongRepository(db_session)
    assert repo.existe_filename("no_existe") is False

def test_get_song_by_filename(db_session):
    repo = SongRepository(db_session)
    song = create_song()
    repo.insert_song(song)
    result = repo.get_song_by_filename("archivo_unico_123")
    assert result is not None
    assert result.songName == "Prueba"

def test_delete_song_by_id(db_session):
    repo = SongRepository(db_session)
    song = create_song()
    repo.insert_song(song)
    assert repo.delete_song(song.idSong) is True
    assert repo.get_song_by_id(song.idSong) is None

def test_delete_song_by_filename(db_session):
    repo = SongRepository(db_session)
    song = create_song()
    repo.insert_song(song)
    assert repo.delete_song_by_filename("archivo_unico_123") is True
    assert repo.get_song_by_filename("archivo_unico_123") is None
