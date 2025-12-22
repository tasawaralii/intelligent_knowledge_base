from pydantic import BaseModel, ConfigDict, field_validator
from datetime import datetime
import re

class User(BaseModel):
    username: str
    email: str
    first_name : str | None = None
    last_name : str | None = None
    model_config = ConfigDict(from_attributes=True)
    
class Token(BaseModel):
    access_token : str
    token_type: str

class TokenData(BaseModel):
    username : str
    model_config = ConfigDict(from_attributes=True)


class NoteBase(BaseModel):
    title: str
    content: str | None = None  # Supports markdown format
    is_pinned: bool = False

class NoteCreate(NoteBase):
    """Model for creating a new note with markdown support"""
    pass

class Note(NoteBase):
    id: int
    created_at: datetime | None = None
    updated_at: datetime | None = None
    model_config = ConfigDict(from_attributes=True)

class Notes(BaseModel):
    notes: list[Note]
    model_config = ConfigDict(from_attributes=True)