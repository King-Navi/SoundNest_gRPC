from datetime import datetime
from typing import Callable
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import select , exists
from dependency_injector.wiring import inject , Provide
from models.mysql.models import Photo


class PhotoRepository:
    def __init__(
        self,
        session_factory: Callable[[], Session],
    ):
        self.session_factory = session_factory

    def add_photo(self, file_name: str, extension: str, id_user: int) -> Photo:
        new_photo = Photo(
            fileName=file_name,
            extension=extension,
            createdAt=datetime.now(),
            idUser=id_user
        )
        try:
            with self.session_factory() as session:
                session.add(new_photo)
                session.commit()
                session.refresh(new_photo)
                return new_photo
        except SQLAlchemyError as e:
            raise e

    def get_photo_by_id(self, photo_id: int) -> Photo | None:
        try:
            with self.session_factory() as session:
                return session.get(Photo, photo_id)
        except SQLAlchemyError as e:
            raise e

    def get_photos_by_user_id(self, id_user: int) -> list[Photo]:
        try:
            with self.session_factory() as session:
                stmt = select(Photo).where(Photo.idUser == id_user)
                return session.scalars(stmt).all()
        except SQLAlchemyError as e:
            raise e

    def has_image(self, id_user: int) -> bool:
        try:
            with self.session_factory() as session:
                stmt = select(exists().where(Photo.idUser == id_user))
                return session.execute(stmt).scalar()
        except SQLAlchemyError as e:
            raise e

    def existe_filename(self, filename: str) -> bool:
        try:
            with self.session_factory() as session:
                stmt = select(exists().where(Photo.fileName == filename))
                return session.execute(stmt).scalar()
        except SQLAlchemyError as e:
            raise e
    def delete_photo(self, photo_id: int) -> bool:
        try:
            with self.session_factory() as session:
                photo = session.get(Photo, photo_id)
                if photo:
                    session.delete(photo)
                    session.commit()
                    return True
                return False
        except SQLAlchemyError as e:
            raise e

    def update_photo(self, photo_id: int, **kwargs) -> Photo | None:
        try:
            with self.session_factory() as session:
                photo = session.get(Photo, photo_id)
                if not photo:
                    return None
                for key, value in kwargs.items():
                    if hasattr(photo, key):
                        setattr(photo, key, value)
                session.commit()
                session.refresh(photo)
                return photo
        except SQLAlchemyError as e:
            raise e
