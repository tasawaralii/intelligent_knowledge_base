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
    tags: list[str] | None = None
    mentions: list[str] | None = None  # @mentions for people, events, concepts
    is_pinned: bool = False
    
    @field_validator('title')
    @classmethod
    def validate_title(cls, v):
        """Validate title is not empty"""
        if v and len(v.strip()) == 0:
            raise ValueError('Title cannot be empty')
        if v and len(v) > 500:
            raise ValueError('Title cannot exceed 500 characters')
        return v
    
    @field_validator('content')
    @classmethod
    def validate_content(cls, v):
        """Validate content length"""
        if v and len(v) > 50000:
            raise ValueError('Content cannot exceed 50000 characters')
        return v
    
    @field_validator('tags')
    @classmethod
    def validate_tags(cls, v):
        """Validate tags"""
        if v:
            if len(v) > 50:
                raise ValueError('Cannot have more than 50 tags')
            for tag in v:
                if len(tag) > 50:
                    raise ValueError('Each tag cannot exceed 50 characters')
        return v


class NoteCreate(NoteBase):
    """Model for creating a new note with markdown support"""
    pass


class NoteUpdate(BaseModel):
    """Model for updating a note - all fields optional"""
    title: str | None = None
    content: str | None = None
    tags: list[str] | None = None
    mentions: list[str] | None = None
    is_pinned: bool | None = None


class NoteVersion(BaseModel):
    """Track version history of notes"""
    id: int
    note_id: int
    title: str
    content: str | None = None
    tags: list[str] | None = None
    mentions: list[str] | None = None
    is_pinned: bool
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class Note(NoteBase):
    id: int
    owner_id: int | None = None
    owner_username: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
    model_config = ConfigDict(from_attributes=True)


class NoteWithVersions(Note):
    """Note with version history"""
    versions: list[NoteVersion] | None = None


class Notes(BaseModel):
    notes: list[Note]
    model_config = ConfigDict(from_attributes=True)


# Relationship Discovery Schemas
class EntityBase(BaseModel):
    name: str
    entity_type: str  # person, place, date, topic, concept
    description: str | None = None
    
    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        """Validate entity name"""
        if not v or len(v.strip()) == 0:
            raise ValueError('Entity name cannot be empty')
        if len(v) > 200:
            raise ValueError('Entity name cannot exceed 200 characters')
        return v.strip()
    
    @field_validator('entity_type')
    @classmethod
    def validate_entity_type(cls, v):
        """Validate entity type"""
        valid_types = ['person', 'place', 'date', 'topic', 'concept']
        if v not in valid_types:
            raise ValueError(f'Entity type must be one of: {", ".join(valid_types)}')
        return v
    
    @field_validator('description')
    @classmethod
    def validate_description(cls, v):
        """Validate description length"""
        if v and len(v) > 1000:
            raise ValueError('Description cannot exceed 1000 characters')
        return v


class EntityCreate(EntityBase):
    pass


class Entity(EntityBase):
    id: int
    owner_id: int | None = None
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class EntityRelationshipBase(BaseModel):
    from_entity_id: int
    to_entity_id: int
    relationship_type: str


class EntityRelationshipCreate(EntityRelationshipBase):
    pass


class EntityRelationship(EntityRelationshipBase):
    id: int
    strength: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class EntityWithRelationships(Entity):
    """Entity with connected entities"""
    relationships_from: list[EntityRelationship] | None = None
    relationships_to: list[EntityRelationship] | None = None


class ConnectionPath(BaseModel):
    """Represents a path between two entities"""
    start_entity: Entity
    end_entity: Entity
    path: list[Entity]
    relationship_chain: list[str]
    total_distance: int


class RelatedNotesCluster(BaseModel):
    """Cluster of related notes based on shared entities"""
    entity_ids: list[int]
    note_ids: list[int]
    shared_entity_count: int
    relevance_score: float
