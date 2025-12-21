from sqlalchemy.orm import Session
from typing import Optional, List
import database.models as models
from schemas import NoteCreate, NoteUpdate, Note
import json


def parse_note(db_note) -> Note:
    """Convert database note to schema with parsed tags"""
    if not db_note:
        return None
    note_dict = db_note.__dict__.copy()
    if db_note.tags:
        try:
            note_dict['tags'] = json.loads(db_note.tags)
        except:
            note_dict['tags'] = []
    else:
        note_dict['tags'] = None
    
    # Get owner username if owner relationship is loaded
    if hasattr(db_note, 'owner') and db_note.owner:
        note_dict['owner_username'] = db_note.owner.username
    
    return Note(**note_dict)


def create_note(db: Session, note: NoteCreate, owner_id: int):
    """Create a new note for a user"""
    tags_str = json.dumps(note.tags) if note.tags else None
    db_note = models.Notes(
        title=note.title,
        content=note.content,
        tags=tags_str,
        is_pinned=note.is_pinned,
        owner_id=owner_id
    )
    db.add(db_note)
    db.commit()
    db.refresh(db_note)
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
    """Update a note"""
    db_note = db.query(models.Notes).filter(
        models.Notes.id == note_id,
        models.Notes.owner_id == owner_id
    ).first()
    
    if not db_note:
        return None
    
    if note_update.title is not None:
        db_note.title = note_update.title
    if note_update.content is not None:
        db_note.content = note_update.content
    if note_update.tags is not None:
        db_note.tags = json.dumps(note_update.tags)
    if note_update.is_pinned is not None:
        db_note.is_pinned = note_update.is_pinned
    
    db.commit()
    db.refresh(db_note)
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
