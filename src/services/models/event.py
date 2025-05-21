from pydantic import BaseModel

class CommentReplyModel(BaseModel):
    id_comment: str
    id_author: int
    name_author: str
    message: str
