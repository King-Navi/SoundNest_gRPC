from datetime import datetime
from typing import Optional
from motor.motor_asyncio import AsyncIOMotorCollection
from pydantic import ValidationError
from pymongo.errors import DuplicateKeyError
from models.mongo.models_mongo import SongDescriptionModel

class SongDescriptionRepository:
    def __init__(self, collection: AsyncIOMotorCollection):
        self.collection = collection

    async def get_description_by_song_id(self, song_id: int) -> Optional[str]:
        """
        Retrieves the song description text for a given song_id.
        
        :param song_id: The ID of the song.
        :return: Description string or None if not found.
        """
        try:
            result = await self.collection.find_one({"songs_id": song_id})
            if result:
                return result.get("description")
            return None
        except Exception:
            return None

    async def add_description(
        self,
        song_id: int,
        author_id: int,
        text: str
    ) -> bool:
        """
        Create or update a SongDescription document.
        - Inserts a new document if none exists for `song_id`.
        - If a document already exists, updates its description (and author_id).
        Returns True on success, False on validation error or unexpected failures.
        """
        try:
            desc = SongDescriptionModel(
                songs_id    = song_id,
                author_id   = author_id,
                description = text
            )
            await self.collection.insert_one(desc.dict(by_alias=True))
            return True
        except ValidationError:
            return False
        except DuplicateKeyError:
            try:
                result = await self.collection.update_one(
                    {"songs_id": song_id},
                    {"$set": {
                        "description": text,
                        "author_id": author_id
                    }}
                )
                return result.modified_count > 0
            except Exception:
                return False
        except Exception:
            return False
    
    async def _create(self, desc: SongDescriptionModel) -> SongDescriptionModel:
        """
        Inserts a new song description into MongoDB.

        :param desc: A validated SongDescriptionModel
        :returns: The saved model (with createdAt from the model and no _id field)
        :raises ValidationError: if desc fails Pydantic validation
        :raises DuplicateKeyError: if songs_id already exists in the collection
        """
        desc = SongDescriptionModel.parse_obj(desc)
        doc = desc.dict(by_alias=True)
        result = await self.collection.insert_one(doc)
        return desc
