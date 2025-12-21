from sqlalchemy import Boolean, Integer, String, ForeignKey, Column, DateTime, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from database.core import Base

class Users(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True)
    username = Column(String, unique=True, index=True)
    first_name = Column(String)
    last_name = Column(String)
    password_hashed = Column(String)
    disabled = Column(Boolean)
    notes = relationship("Notes", back_populates="owner")


class Notes(Base):
    __tablename__ = 'notes'
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    content = Column(Text, nullable=True)
    tags = Column(String, nullable=True)  # Store as JSON string
    is_pinned = Column(Boolean, default=False)
    owner_id = Column(Integer, ForeignKey('users.id'), index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    owner = relationship("Users", back_populates="notes")