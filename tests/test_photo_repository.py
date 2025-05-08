import pytest
from src.repository.photo_repository import PhotoRepository
from src.models.mysql.models import Base, Photo

from src.config.connection_mysql import engine , SessionLocal

@pytest.fixture(scope="function")
def db_session():
    """Crea una sesión con rollback al terminar cada test."""
    connection = engine.connect()
    transaction = connection.begin()
    session = SessionLocal(bind=connection)

    yield session  # lo que retorne aquí será inyectado al test

    session.close()
    transaction.rollback()
    connection.close()

def test_add_and_get_photo(db_session):
    repo = PhotoRepository(session=db_session)

    # ACT: agregamos una foto
    new_photo = repo.add_photo("test_file.jpg", "jpg", id_user=1)

    # ASSERT: verificamos que exista y tenga ID
    assert new_photo.idPhoto is not None
    assert new_photo.fileName == "test_file.jpg"

    # GET: obtener la misma foto
    retrieved = repo.get_photo_by_id(new_photo.idPhoto)
    assert retrieved is not None
    assert retrieved.fileName == "test_file.jpg"

def test_get_photos_by_user_id(db_session):
    repo = PhotoRepository(session=db_session)

    # ACT: agregamos 2 fotos para id_user=2
    repo.add_photo("photo1.jpg", "jpg", id_user=2)
    repo.add_photo("photo2.jpg", "jpg", id_user=2)

    photos = repo.get_photos_by_user_id(2)

    # ASSERT: debe haber al menos 2 fotos para id_user=2
    assert len(photos) >= 2
    filenames = [p.fileName for p in photos]
    assert "photo1.jpg" in filenames
    assert "photo2.jpg" in filenames

def test_update_photo(db_session):
    repo = PhotoRepository(session=db_session)

    # ACT: crear una foto
    photo = repo.add_photo("old_name.jpg", "jpg", id_user=1)

    # ACT: actualizar su fileName
    updated = repo.update_photo(photo.idPhoto, fileName="new_name.jpg")

    # ASSERT: verificar que se actualizó
    assert updated is not None
    assert updated.fileName == "new_name.jpg"

def test_delete_photo(db_session):
    repo = PhotoRepository(session=db_session)

    # ACT: crear una foto
    photo = repo.add_photo("to_delete.jpg", "jpg", id_user=1)

    # ACT: eliminar la foto
    deleted = repo.delete_photo(photo.idPhoto)

    # ASSERT: confirmar que se eliminó
    assert deleted is True
    assert repo.get_photo_by_id(photo.idPhoto) is None

def test_has_image_returns_false_when_no_images(db_session):
    repo = PhotoRepository(session=db_session)
    user_id = 2
    assert repo.has_image(user_id) is False

def test_has_image_returns_true_when_image_exists(db_session):
    repo = PhotoRepository(session=db_session)
    user_id = 1
    repo.add_photo("test_image.jpg", "jpg", user_id)

    assert repo.has_image(user_id) is True

def test_exist_file_returns_true_when_image_exists(db_session):
    repo = PhotoRepository(session=db_session)
    user_id = 1
    file = "test_image.jpg"
    repo.add_photo(file, "jpg", user_id)

    assert repo.existe_filename(file) is True