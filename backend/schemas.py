from pydantic import BaseModel, ConfigDict
from datetime import datetime, date
from typing import List, Optional

class User(BaseModel):
    username: str
    email: str
    first_name : str | None = None
    last_name : str | None = None
    model_config = ConfigDict(from_attributes=True)
    
class PersonBase(BaseModel):
    first_name: str
    last_name: str | None = None
    father_name: str | None = None
    slug : str | None = None
    cnic: str | None = None
    phone_number: str | None = None
    email: str | None = None
    address: str | None = None
    city: str | None = None
    country: str | None = None
    date_of_birth: date | None = None
    gender: str | None = None
    picture_url: str | None = None


class PersonCreate(PersonBase):
    """Input model for creating a person"""
    pass


class PersonRead(PersonBase):
    id: int
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)


class PersonResponse(PersonBase):
    """Response model for Person - same as PersonRead"""
    id: int
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)


class PersonUpdate(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    father_name: str | None = None
    cnic: str | None = None
    phone_number: str | None = None
    email: str | None = None
    address: str | None = None
    city: str | None = None
    country: str | None = None
    date_of_birth: date | None = None
    gender: str | None = None
    picture_url: str | None = None


class PersonChange(BaseModel):
    field: str
    old_value: str | None
    new_value: str | None
    changed_at: datetime
    model_config = ConfigDict(from_attributes=True)


class PersonUpdateResponse(BaseModel):
    person: PersonRead
    changes: list[PersonChange]


class PersonPhoneUpdate(BaseModel):
    phone_number: str


class PersonCnicUpdate(BaseModel):
    cnic: str


class PersonNameUpdate(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    father_name: str | None = None


class Persons(BaseModel):
    persons: list[PersonRead]
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


class Mention(BaseModel):
    slug: str
    type: str  # 'person', 'place', 'event'
    new: bool = False  # Is this a new entity being created?

class AllMentions(BaseModel):
    persons: List[Mention] = []
    places: List[Mention] = []
    events: List[Mention] = []

class NoteCreate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    is_pinned: bool = False

class Note(BaseModel):
    id: int
    title: Optional[str]
    content: Optional[str]
    mentions: AllMentions
    is_pinned: bool
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)


class Notes(BaseModel):
    notes: list[Note]
    model_config = ConfigDict(from_attributes=True)


class PlaceBase(BaseModel):
    name: str
    slug: str | None = None
    place_type: str | None = None
    address: str | None = None
    city: str | None = None
    country: str | None = None
    description: str | None = None


class PlaceCreate(PlaceBase):
    """Input model for creating a place"""
    pass


class PlaceResponse(PlaceBase):
    """Response model for Place"""
    id: int
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)


class EventBase(BaseModel):
    title: str
    slug: str | None = None
    event_type: str | None = None
    start_datetime: datetime
    end_datetime: datetime | None = None
    place_id: int | None = None
    description: str | None = None


class EventCreate(EventBase):
    """Input model for creating an event"""
    pass


class EventResponse(EventBase):
    """Response model for Event"""
    id: int
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)


class FactEntity(BaseModel):
    """Entity information within a fact"""
    type: str  # 'person', 'place', 'event'
    id: int
    name: str


class FactDetail(BaseModel):
    """Detailed fact information for rendering @f.{id} in notes"""
    id: int
    source: FactEntity
    target: FactEntity
    relation_type: str
    confidence: int
    description: str
    created_at: str  # ISO format datetime
