from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from backend.app.db.models import ReactionType

class ReactionCreate(BaseModel):
    reaction_type: ReactionType

class CommentCreate(BaseModel):
    content: str

class ReactionResponse(BaseModel):
    id: int
    woulate_id: int
    user_id: int
    reaction_type: ReactionType
    created_at: datetime
    
    class Config:
        from_attributes = True

class CommentResponse(BaseModel):
    id: int
    woulate_id: int
    user_id: int
    content: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    is_deleted: bool = False
    
    class Config:
        from_attributes = True

class WoulatDetailResponse(BaseModel):
    id: int
    full_name: str
    job_title: str
    job_description: str
    reactions: List[ReactionResponse]
    comments: List[CommentResponse]
    
    class Config:
        from_attributes = True