from sqlalchemy.orm import Session , joinedload
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import select , exists
from dependency_injector.wiring import inject, Provide
from models.mysql.models import Song
from typing import Callable
import logging

class SongRepository:
    def __init__(self,
                  session_factory: Callable[[], Session]):
        self.session_factory = session_factory

    def existe_filename(self, filename: str) ->bool:
        try:
            with self.session_factory() as session:
                stmt = select(exists().where(Song.fileName == filename))
                return session.execute(stmt).scalar()
        except SQLAlchemyError as e:
            logging.info(e)
            raise e

    def insert_song(self, song: Song) -> Song:
        """
        Inserts a new Song record into the database and returns
        the fully populated instance (including any auto-generated fields).

        :param song: A Song instance without its primary key set.
        :returns: The same Song instance, now with all database-generated fields populated.
        :raises SQLAlchemyError: If the operation fails and is rolled back.
        """
        try:
            with self.session_factory() as session:
                session.add(song)
                session.commit()
                session.refresh(song)
                return song
        except SQLAlchemyError as e:
            logging.info(e)
            raise e

    def delete_song(self, id_song: int) -> bool:
        try:
            with self.session_factory() as session:
                song = session.get(Song, id_song)
                if not song or song.isDeleted == 1:
                    return True
                song.isDeleted = 1
                session.commit()
                return True
        except SQLAlchemyError as e:
            raise e

    def get_song_by_id(self, id_song: int) -> Song | None:
        try:
            with self.session_factory() as session:
                stmt = (
                    session.query(Song)
                           .options(joinedload(Song.SongExtension_))
                           .filter(Song.idSong == id_song)
                )
                return stmt.one_or_none()
        except SQLAlchemyError as e:
            logging.info(e)
            raise e

    def get_song_by_filename(self, filename: str) -> Song | None:
        try:
            with self.session_factory() as session:
                stmt = select(Song).where(Song.fileName == filename)
                return session.execute(stmt).scalars().first()
        except SQLAlchemyError as e:
            raise e

    def delete_song_by_filename(self, filename: str) -> bool:
        try:
            with self.session_factory() as session:
                stmt = select(Song).where(Song.fileName == filename)
                song = session.execute(stmt).scalars().first()
                if not song:
                    return False
                session.delete(song)
                session.commit()
                return True
        except SQLAlchemyError as e:
            raise e