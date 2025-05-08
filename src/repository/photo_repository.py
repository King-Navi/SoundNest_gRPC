from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import select , exists
from dependency_injector.wiring import inject
from models.mysql.models import Photo

class PhotoRepository:
    @inject
    def __init__(self, session: Session):
        self.session = session

    def add_photo(self, file_name: str, extension: str, id_user: int) -> Photo:
        new_photo = Photo(
            fileName=file_name,
            extension=extension,
            createdAt=datetime.now(),
            idUser=id_user
        )
        try:
            self.session.add(new_photo)
            self.session.commit()
            self.session.refresh(new_photo)
        except SQLAlchemyError as e:
            self.session.rollback()
            raise e
        return new_photo

    def get_photo_by_id(self, photo_id: int) -> Photo | None:
        try:
            return self.session.get(Photo, photo_id)
        except SQLAlchemyError as e:
            raise e

    def get_photos_by_user_id(self, id_user: int) -> list[Photo]:
        try:
            stmt = select(Photo).where(Photo.idUser == id_user)
            result = self.session.scalars(stmt).all()
            return result
        except SQLAlchemyError as e:
            raise e

    def has_image(self, id_user: int)->bool:
        try: 
            stmt = select(exists().where(Photo.idUser == id_user))
            result = self.session.execute(stmt).scalar()
            return result
        except SQLAlchemyError as e:
            raise e

    def existe_filename(self, filename: str) ->bool:
        try:
            stmt = select(exists().where(Photo.fileName == filename))
            result = self.session.execute(stmt).scalar()
            return result
        except SQLAlchemyError as e:
            raise e

    def delete_photo(self, photo_id: int) -> bool:
        try:
            photo = self.get_photo_by_id(photo_id)
            if photo:
                self.session.delete(photo)
                self.session.commit()
                return True
            return False
        except SQLAlchemyError as e:
            self.session.rollback()
            raise e

    def update_photo(self, photo_id: int, **kwargs) -> Photo | None:
        try:
            photo = self.get_photo_by_id(photo_id)
            if not photo:
                return None
            for key, value in kwargs.items():
                if hasattr(photo, key):
                    setattr(photo, key, value)
            self.session.commit()
            self.session.refresh(photo)
            return photo
        except SQLAlchemyError as e:
            self.session.rollback()
            raise e
