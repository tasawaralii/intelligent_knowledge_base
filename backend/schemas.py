from pydantic import BaseModel, ConfigDict
from datetime import datetime

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
    content: str | None = None
    tags: list[str] | None = None
    is_pinned: bool = False


class NoteCreate(NoteBase):
    """Model for creating a new note"""
    pass


class NoteUpdate(BaseModel):
    """Model for updating a note - all fields optional"""
    title: str | None = None
    content: str | None = None
    tags: list[str] | None = None
    is_pinned: bool | None = None


class Note(NoteBase):
    id: int
    owner_id: int | None = None
    owner_username: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
    model_config = ConfigDict(from_attributes=True)


class Notes(BaseModel):
    notes: list[Note]
    model_config = ConfigDict(from_attributes=True)
