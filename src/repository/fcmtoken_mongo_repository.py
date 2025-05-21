from typing import Optional
from datetime import datetime
from dependency_injector.wiring import Provider, inject
from motor.motor_asyncio import AsyncIOMotorCollection
from models.mongo.models_mongo import FcmTokenModel

class FcmTokenRepository:
    @inject
    def __init__(self, collection: AsyncIOMotorCollection):
        self.collection = collection

    async def get_by_user_id(self, user_id: int) -> Optional[dict]:
        """
        Retrieves a FCM token document by user_id.
        """
        return await self.collection.find_one({"user_id": user_id})

    async def create(self, token_data: FcmTokenModel) -> dict:
        """
        Inserts a new FCM token document.
        """
        result = await self.collection.insert_one(token_data.dict())
        return {**token_data.dict(), "_id": result.inserted_id}

    async def update_by_user_id(self, user_id: int, new_data: dict) -> Optional[dict]:
        """
        Updates token info by user_id if it exists.
        """
        update_data = {
            "$set": {
                **new_data,
                "updatedAt": datetime.utcnow()
            }
        }
        return await self.collection.find_one_and_update(
            {"user_id": user_id},
            update_data,
            return_document=True
        )

    async def exists(self, user_id: int) -> bool:
        """
        Checks if a token exists for the user.
        """
        result = await self.collection.find_one({"user_id": user_id})
        return result is not None
