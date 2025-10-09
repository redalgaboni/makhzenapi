from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, Text, Enum, Boolean, UniqueConstraint
from .base import Base
from sqlalchemy.sql import func
from enum import Enum as PyEnum

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    full_name = Column(String)
    hashed_password = Column(String)

class Jihate(Base):
    __tablename__ = "jihate"

    id = Column(Integer, primary_key=True, index=True)
    jiha_id = Column(Integer, nullable=False)  
    jiha = Column(String, nullable=False)
    wilaya_id = Column(Integer, nullable=False)
    wilaya = Column(String, nullable=False)
    assima_jiha = Column(String)
    assima_jiha_id = Column(Integer)

class Woulate(Base):
    __tablename__ = "woulate"

    id = Column(Integer, primary_key=True, index=True)
    jiha_id = Column(Integer, index=True)      # ← from jihate.jiha_id
    wilaya_id = Column(Integer, index=True)    # ← from jihate.wilaya_id

    idara = Column(String, nullable=False)
    full_name = Column(String, nullable=False)
    job_title = Column(String, nullable=False)
    job_description = Column(String, nullable=False)

    amala_jamaa_id = Column(Integer)
    amala = Column(String)
    active = Column(Boolean, default=True)
    assignment_date = Column(String) # date of assignment if any
    assignment_year = Column(Integer)

class AmalateJamaate(Base):
    __tablename__ = "amalate_jamaate"

    id = Column(Integer, primary_key=True, index=True)
    amala_jamaa_id = Column(Integer, nullable=False)
    amala_jamaa = Column(String, nullable=False)
    wilaya_id = Column(Integer, nullable=False)
    wilaya = Column(String, nullable=False)
    jiha_id = Column(Integer, nullable=False)
    jiha = Column(String, nullable=False)

class ReactionType(str, PyEnum):
    LIKE = "like"
    DISLIKE = "dislike"
    LOVE = "love"
    ANGRY = "angry"
    CRY = "cry"

class Reaction(Base):
    __tablename__ = "reactions"
    
    id = Column(Integer, primary_key=True, index=True)
    woulate_id = Column(Integer, ForeignKey("woulate.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    reaction_type = Column(Enum(ReactionType), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Unique constraint: one reaction per user per woulat
    __table_args__ = (
        UniqueConstraint('woulate_id', 'user_id', name='uq_user_woulat_reaction'),
    )

class Comment(Base):
    __tablename__ = "comments"
    
    id = Column(Integer, primary_key=True, index=True)
    woulate_id = Column(Integer, ForeignKey("woulate.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    is_deleted = Column(Boolean, default=False)  # Soft delete