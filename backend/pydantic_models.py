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

class WoulateCreate(BaseModel):
    
    full_name: str
    job_description: str
    idara: str
    jiha: Optional[str] = None
    wilaya: Optional[str] = None
    amala_jamaa_id: Optional[int] = None
    amala: Optional[str] = None
    assignment_date: str
    assignment_year: int
    active: bool = True

class WoulateSearchResult(BaseModel):
    
    id: int
    full_name: str
    job_title: Optional[str] = None
    job_description: str
    jiha: str
    wilaya: str
    assignment_date: Optional[str] = None
    assignment_year: Optional[int] = None
    
    class Config:
        from_attributes = True