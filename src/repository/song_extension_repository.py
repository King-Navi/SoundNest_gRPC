from typing import Optional, Callable
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from dependency_injector.wiring import inject , Provide
from models.mysql.models import SongExtension
import logging
class SongExtensionRepository:
    def __init__(
        self,
        session_factory: Callable[[], Session],
    ):
        self.session_factory = session_factory

    def get_extension_id_by_name(self, extension_name: str) -> Optional[int]:
        try:
            with self.session_factory() as session:
                extension_name = extension_name.strip().lower()
                result = session.query(SongExtension).filter_by(extensionName=extension_name).first()
                return result.idSongExtension if result else -1
        except SQLAlchemyError as e:
            raise e
    
    def get_extension_name_by_id(self, id_extension: int) -> Optional[str]:
        try:
            with self.session_factory() as session:
                result = session.query(SongExtension).filter_by(idSongExtension=id_extension).first()
                return result.extensionName if result else None
        except SQLAlchemyError as e:
            raise e
