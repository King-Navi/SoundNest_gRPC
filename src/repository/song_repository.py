from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import select , exists
from dependency_injector.wiring import inject
from models.mysql.models import Song
class SongRepository:
    @inject
    def __init__(self, session: Session):
        self.session = session

    def existe_filename(self, filename: str) ->bool:
        try:
            stmt = select(exists().where(Song.fileName == filename))
            result = self.session.execute(stmt).scalar()
            return result
        except SQLAlchemyError as e:
            raise e

    def insert_song(self, song: Song) -> bool:
        try:
            self.session.add(song)
            self.session.commit()
            return True
        except SQLAlchemyError as e:
            self.session.rollback()
            raise e

    def delete_song(self, id_song: int) -> bool:
        try:
            song = self.session.get(Song, id_song)
            if not song:
                return False
            self.session.delete(song)
            self.session.commit()
            return True
        except SQLAlchemyError as e:
            self.session.rollback()
            raise e

    def get_song_by_id(self, id_song: int) -> Song | None:
        try:
            return self.session.get(Song, id_song)
        except SQLAlchemyError as e:
            raise e

    def get_song_by_filename(self, filename: str) -> Song | None:
        try:
            stmt = select(Song).where(Song.fileName == filename)
            result = self.session.execute(stmt).scalars().first()
            return result
        except SQLAlchemyError as e:
            raise e

    def delete_song_by_filename(self, filename: str) -> bool:
        try:
            stmt = select(Song).where(Song.fileName == filename)
            song = self.session.execute(stmt).scalars().first()
            if not song:
                return False
            self.session.delete(song)
            self.session.commit()
            return True
        except SQLAlchemyError as e:
            self.session.rollback()
            raise e