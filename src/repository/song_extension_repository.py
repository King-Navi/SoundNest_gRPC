from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from dependency_injector.wiring import inject
from models.mysql.models import SongExtension
class SongExtensionRepository:
    @inject
    def __init__(self, session: Session):
        self.session = session

    def get_extension_id_by_name(self, extension_name: str) -> Optional[int]:
        try:
            extension_name = extension_name.strip().lower()
            result = self.session.query(SongExtension).filter_by(extensionName=extension_name).first()
            if result:
                return result.idSongExtension
            return -1
        except SQLAlchemyError as e:
            raise e
    
    def get_extension_name_by_id(self, id_extension: int) -> Optional[str]:
        try:
            result = (
                self.session
                    .query(SongExtension)
                    .filter_by(idSongExtension=id_extension)
                    .first()
            )
            if result:
                return result.extensionName
            return None
        except SQLAlchemyError as e:
            raise
