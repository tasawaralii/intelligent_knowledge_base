from sqlalchemy.orm import Session
from typing import Optional, List
import database.models as models
from schemas import NoteCreate, Note
import json
import re


def extract_mentions(content: str) -> list[str]:
    """Extract @mentions from note content"""
    if not content:
        return []
    # Find all @username patterns
    mentions = re.findall(r'@\w+', content)
    return list(set(mentions))  # Remove duplicates


def parse_note(db_note) -> Note | None:
    """Convert database note to schema with parsed tags and mentions"""
    if not db_note:
        return None
    
    return Note(
        id=db_note.id,
        title=db_note.title,
        content=db_note.content,
        is_pinned=db_note.is_pinned,
        created_at=db_note.created_at,
        updated_at=db_note.updated_at
    )

def create_note(db: Session, note: NoteCreate, owner_id: int):
    """Create a new note for a user with markdown support"""
    try:
        db_note = models.Notes(
            title=note.title,
            content=note.content,
            is_pinned=note.is_pinned,
            owner_id=owner_id
        )
        db.add(db_note)
        db.commit()
        db.refresh(db_note)
        
        return parse_note(db_note)
    except Exception as e:
        db.rollback()
        raise e


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