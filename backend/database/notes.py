from sqlalchemy.orm import Session
from typing import Optional, List
import database.models as models
from schemas import NoteCreate, NoteUpdate, Note, NoteVersion
import json
import re


def extract_mentions(content: str) -> list[str]:
    """Extract @mentions from note content"""
    if not content:
        return []
    # Find all @username patterns
    mentions = re.findall(r'@\w+', content)
    return list(set(mentions))  # Remove duplicates


def parse_note(db_note) -> Note:
    """Convert database note to schema with parsed tags and mentions"""
    if not db_note:
        return None
    
    # Extract only relevant fields, avoid SQLAlchemy internal state
    tags = None
    if db_note.tags:
        try:
            tags = json.loads(db_note.tags)
        except:
            tags = []
    
    mentions = None
    if db_note.mentions:
        try:
            mentions = json.loads(db_note.mentions)
        except:
            mentions = []
    
    owner_username = None
    if hasattr(db_note, 'owner') and db_note.owner:
        owner_username = db_note.owner.username
    
    return Note(
        id=db_note.id,
        title=db_note.title,
        content=db_note.content,
        tags=tags,
        mentions=mentions,
        is_pinned=db_note.is_pinned,
        owner_id=db_note.owner_id,
        owner_username=owner_username,
        created_at=db_note.created_at,
        updated_at=db_note.updated_at
    )


def create_note_version(db: Session, note_id: int, owner_id: int, title: str, content: str | None, tags: str | None, mentions: str | None, is_pinned: bool):
    """Create a version record for note changes"""
    version = models.NoteVersion(
        note_id=note_id,
        owner_id=owner_id,
        title=title,
        content=content,
        tags=tags,
        mentions=mentions,
        is_pinned=is_pinned
    )
    db.add(version)
    db.commit()


def create_note(db: Session, note: NoteCreate, owner_id: int):
    """Create a new note for a user with markdown support"""
    tags_str = json.dumps(note.tags) if note.tags else None
    # Extract mentions from content if not provided
    mentions = note.mentions or extract_mentions(note.content or "")
    mentions_str = json.dumps(mentions) if mentions else None
    
    db_note = models.Notes(
        title=note.title,
        content=note.content,
        tags=tags_str,
        mentions=mentions_str,
        is_pinned=note.is_pinned,
        owner_id=owner_id
    )
    db.add(db_note)
    db.commit()
    db.refresh(db_note)
    
    # Create initial version record
    create_note_version(db, db_note.id, owner_id, note.title, note.content, tags_str, mentions_str, note.is_pinned)
    
    return parse_note(db_note)


def get_note(db: Session, note_id: int, owner_id: Optional[int] = None):
    """Get a single note by ID, optionally verify ownership"""
    query = db.query(models.Notes).filter(models.Notes.id == note_id)
    if owner_id:
        query = query.filter(models.Notes.owner_id == owner_id)
    db_note = query.first()
    return parse_note(db_note)


def get_user_notes(db: Session, owner_id: int, skip: int = 0, limit: int = 100):
    """Get all notes for a user with pagination"""
    notes = db.query(models.Notes).filter(
        models.Notes.owner_id == owner_id
    ).offset(skip).limit(limit).all()
    return [parse_note(note) for note in notes]


def get_pinned_notes(db: Session, owner_id: int):
    """Get all pinned notes for a user"""
    notes = db.query(models.Notes).filter(
        models.Notes.owner_id == owner_id,
        models.Notes.is_pinned == True
    ).all()
    return [parse_note(note) for note in notes]


def update_note(db: Session, note_id: int, note_update: NoteUpdate, owner_id: int):
    """Update a note and create version record"""
    db_note = db.query(models.Notes).filter(
        models.Notes.id == note_id,
        models.Notes.owner_id == owner_id
    ).first()
    
    if not db_note:
        return None
    
    # Update fields
    if note_update.title is not None:
        db_note.title = note_update.title
    if note_update.content is not None:
        db_note.content = note_update.content
    if note_update.tags is not None:
        db_note.tags = json.dumps(note_update.tags)
    if note_update.mentions is not None:
        db_note.mentions = json.dumps(note_update.mentions)
    elif note_update.content is not None:
        # Auto-extract mentions if content changed and mentions not explicitly provided
        mentions = extract_mentions(note_update.content)
        db_note.mentions = json.dumps(mentions) if mentions else None
    if note_update.is_pinned is not None:
        db_note.is_pinned = note_update.is_pinned
    
    db.commit()
    db.refresh(db_note)
    
    # Create version record for changes
    create_note_version(db, db_note.id, owner_id, db_note.title, db_note.content, db_note.tags, db_note.mentions, db_note.is_pinned)
    
    return parse_note(db_note)


def delete_note(db: Session, note_id: int, owner_id: int):
    """Delete a note"""
    db_note = db.query(models.Notes).filter(
        models.Notes.id == note_id,
        models.Notes.owner_id == owner_id
    ).first()
    
    if not db_note:
        return None
    
    db.delete(db_note)
    db.commit()
    return parse_note(db_note)


def get_note_versions(db: Session, note_id: int, owner_id: int):
    """Get version history for a note"""
    versions = db.query(models.NoteVersion).filter(
        models.NoteVersion.note_id == note_id,
        models.NoteVersion.owner_id == owner_id
    ).order_by(models.NoteVersion.created_at.desc()).all()
    return versions
