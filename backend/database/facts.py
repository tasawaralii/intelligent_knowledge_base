"""
Facts Model - Stores extracted factual relationships from notes
Fact: A relationship between two entities extracted from natural language

Examples:
- Person A "studies at" Place B (extracted from note mentioning both)
- Person A "attended" Event B
- Person A "works with" Person B (both mentioned in same context/note)
"""

from sqlalchemy import Integer, String, ForeignKey, Column, DateTime, Text, Table, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
from database.core import Base
import enum

class RelationType(str, enum.Enum):
    """Types of relations that can exist between entities"""
    # Person-Place relations
    STUDIES_AT = "studies_at"
    WORKS_AT = "works_at"
    LIVES_AT = "lives_at"
    VISITS = "visits"
    OWNS = "owns"
    MANAGES = "manages"
    
    # Person-Event relations
    ATTENDS = "attends"
    ORGANIZES = "organizes"
    PARTICIPATES = "participates"
    HOSTS = "hosts"
    
    # Person-Person relations
    KNOWS = "knows"
    WORKS_WITH = "works_with"
    RELATED_TO = "related_to"
    FRIEND_OF = "friend_of"
    COLLEAGUE_OF = "colleague_of"
    SUPERVISOR_OF = "supervisor_of"
    SUBORDINATE_OF = "subordinate_of"
    
    # Place-Event relations
    LOCATED_AT = "located_at"
    HOSTED_AT = "hosted_at"
    
    # Generic relation (for unclassified mentions)
    RELATED = "related"


class Facts(Base):
    """
    Facts table - stores extracted relationships between entities
    
    A fact represents a relationship between two entities discovered from the notes system.
    Each fact has:
    - A source entity (person, place, or event)
    - A target entity (person, place, or event)
    - A relation type
    - Evidence (notes that support this fact)
    - Confidence score (based on frequency and context)
    """
    __tablename__ = "facts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True)
    
    # Source entity
    source_type = Column(String(50), nullable=False)  # 'person', 'place', 'event'
    source_id = Column(Integer, nullable=False, index=True)  # ID of person, place, or event
    
    # Target entity
    target_type = Column(String(50), nullable=False)  # 'person', 'place', 'event'
    target_id = Column(Integer, nullable=False, index=True)  # ID of person, place, or event
    
    # Relation type
    relation_type = Column(String(50), nullable=False, index=True)  # e.g., 'studies_at', 'works_at'
    
    # Evidence and confidence
    confidence_score = Column(Integer, default=1)  # Number of times this fact appears
    description = Column(Text, nullable=True)  # Natural language description of the fact
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Store original fact text from #bf...#ef blocks
    extracted_from_text = Column(Text, nullable=True)
    
    # Relationships
    owner = relationship("Users", foreign_keys=[user_id])
    note_facts = relationship("NoteFact", back_populates="fact", cascade="all, delete-orphan")


class NoteFact(Base):
    """
    Junction table linking facts to specific notes where they were extracted
    Allows tracking of fact position in note content for dynamic rendering
    """
    __tablename__ = "note_facts"
    
    id = Column(Integer, primary_key=True, index=True)
    note_id = Column(Integer, ForeignKey("notes.id", ondelete="CASCADE"), index=True)
    fact_id = Column(Integer, ForeignKey("facts.id", ondelete="CASCADE"), index=True)
    position_in_note = Column(Integer, nullable=True)  # Character position where @f.X appears
    extracted_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    note = relationship("Notes", back_populates="note_facts")
    fact = relationship("Facts", back_populates="note_facts")


class FactEvidence(Base):
    """
    Evidence table - links facts to the notes that support them
    Tracks which notes contain evidence for each fact
    """
    __tablename__ = "fact_evidence"
    
    id = Column(Integer, primary_key=True, index=True)
    fact_id = Column(Integer, ForeignKey("facts.id", ondelete="CASCADE"), index=True)
    note_id = Column(Integer, ForeignKey("notes.id", ondelete="CASCADE"), index=True)
    
    # Context from the note
    context_text = Column(Text, nullable=True)  # The relevant sentence/section from note
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    fact = relationship("Facts", foreign_keys=[fact_id])
    note = relationship("Notes", foreign_keys=[note_id])
