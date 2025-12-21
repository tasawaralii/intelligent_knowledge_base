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
    
    @field_validator('mentions', mode='before')
    @classmethod
    def extract_mentions(cls, v):
        """Extract @mentions from content or validate existing mentions"""
        if isinstance(v, list):
            return v
        return None


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
