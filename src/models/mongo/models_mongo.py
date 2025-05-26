from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class FcmTokenModel(BaseModel):
    user_id: int
    token: str
    device: Optional[str] = Field(default="android", pattern="^(android|ios|web)$")
    platform_version: Optional[str] = None
    app_version: Optional[str] = None
    createdAt: Optional[datetime] = Field(default_factory=datetime.utcnow)
    updatedAt: Optional[datetime] = Field(default_factory=datetime.utcnow)

class SongDescriptionModel(BaseModel):
    songs_id:   int       = Field(..., description="Unique song description ID")
    author_id:  int       = Field(..., description="ID of the author")
    description:str      = Field(..., description="Description text")
    createdAt:  datetime  = Field(default_factory=datetime.utcnow,
                                  description="Creation timestamp")
    model_config = {
        "validate_by_name": True,
        "from_attributes":  True,
    }
