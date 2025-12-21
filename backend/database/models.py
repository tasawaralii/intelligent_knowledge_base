from sqlalchemy import Boolean, Integer, String, ForeignKey, Column, DateTime, Text, Table
from sqlalchemy.orm import relationship
from datetime import datetime
from database.core import Base

# Association table for many-to-many relationship between Notes and Entities
note_entity_association = Table(
    'note_entity_association',
    Base.metadata,
    Column('note_id', Integer, ForeignKey('notes.id'), primary_key=True),
    Column('entity_id', Integer, ForeignKey('entities.id'), primary_key=True)
)

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
    note_versions = relationship("NoteVersion", back_populates="owner")
    entities = relationship("Entity", back_populates="owner")
    entity_relationships = relationship("EntityRelationship", back_populates="owner")


class Notes(Base):
    __tablename__ = 'notes'
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    content = Column(Text, nullable=True)  # Markdown supported
    tags = Column(String, nullable=True)  # Store as JSON string
    mentions = Column(String, nullable=True)  # Store @mentions as JSON string
    is_pinned = Column(Boolean, default=False)
    owner_id = Column(Integer, ForeignKey('users.id'), index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    owner = relationship("Users", back_populates="notes")
    versions = relationship("NoteVersion", back_populates="note", cascade="all, delete-orphan")
    entities = relationship("Entity", secondary=note_entity_association, back_populates="notes")


class NoteVersion(Base):
    __tablename__ = 'note_versions'
    
    id = Column(Integer, primary_key=True, index=True)
    note_id = Column(Integer, ForeignKey('notes.id'), index=True)
    owner_id = Column(Integer, ForeignKey('users.id'))
    title = Column(String)
    content = Column(Text, nullable=True)
    tags = Column(String, nullable=True)
    mentions = Column(String, nullable=True)
    is_pinned = Column(Boolean)
    created_at = Column(DateTime, default=datetime.utcnow)
    note = relationship("Notes", back_populates="versions")
    owner = relationship("Users", back_populates="note_versions")


class Entity(Base):
    """Extracted entities from notes (people, places, dates, topics)"""
    __tablename__ = 'entities'
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    entity_type = Column(String, index=True)  # person, place, date, topic, concept
    description = Column(Text, nullable=True)
    owner_id = Column(Integer, ForeignKey('users.id'), index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    owner = relationship("Users", back_populates="entities")
    notes = relationship("Notes", secondary=note_entity_association, back_populates="entities")
    relationships_from = relationship("EntityRelationship", foreign_keys="EntityRelationship.from_entity_id", back_populates="from_entity")
    relationships_to = relationship("EntityRelationship", foreign_keys="EntityRelationship.to_entity_id", back_populates="to_entity")


class EntityRelationship(Base):
    """Graph-based relationships between entities"""
    __tablename__ = 'entity_relationships'
    
    id = Column(Integer, primary_key=True, index=True)
    from_entity_id = Column(Integer, ForeignKey('entities.id'), index=True)
    to_entity_id = Column(Integer, ForeignKey('entities.id'), index=True)
    relationship_type = Column(String)  # related_to, mentioned_with, same_as, etc.
    strength = Column(Integer, default=1)  # Connection strength (how many notes mention both)
    owner_id = Column(Integer, ForeignKey('users.id'), index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    from_entity = relationship("Entity", foreign_keys=[from_entity_id], back_populates="relationships_from")
    to_entity = relationship("Entity", foreign_keys=[to_entity_id], back_populates="relationships_to")
    owner = relationship("Users", back_populates="entity_relationships")