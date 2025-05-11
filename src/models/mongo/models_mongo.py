from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class AdditionalInfoModel(BaseModel):
    userId: int
    info: dict

class ResponseModel(BaseModel):
    user: str
    message: str
    timestamp: Optional[datetime] = Field(default_factory=datetime.utcnow)
    parent_id: Optional[str]
    responses: Optional[List[str]] = []

class CommentModel(BaseModel):
    song_id: int
    user: str
    message: str
    timestamp: Optional[datetime] = Field(default_factory=datetime.utcnow)
    parent_id: Optional[str]
    responses: Optional[List[ResponseModel]] = []

class NotificationModel(BaseModel):
    sender: str
    user_id: int
    user: str
    notification: str
    relevance: Optional[str] = 'low'
    createdAt: Optional[datetime] = Field(default_factory=datetime.utcnow)
    read: Optional[bool] = False
