from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from database.core import get_db
from dependencies import get_current_user
from database.models import Users, Notes
from schemas import Note, NoteCreate
from services import note_service

router = APIRouter(prefix="/note", tags=["Note"])

@router.post("/", response_model=Note, status_code=status.HTTP_201_CREATED)
def create_note(
    note: NoteCreate,
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user)
):
    """
    Create a new note with automatic entity linking
    
    Example content:
    ```
    Met with @p.john_doe at @pl.office.
    Discussed @e.product_launch plans.
    New contact: @n.p.sarah_smith
    ```
    """
    return note_service.create_note(db, note, current_user.id)


@router.get("/", response_model=List[Note])
def get_notes(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user)
):
    """Get all notes for current user"""
    return note_service.get_notes(db, current_user.id, skip, limit)


@router.get("/{note_id}", response_model=Note)
def get_note(
    note_id: int,
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user)
):
    """Get a specific note with all linked entities"""
    note = note_service.get_note(db, note_id, current_user.id)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    return note


@router.put("/{note_id}", response_model=Note)
def update_note(
    note_id: int,
    note: NoteCreate,
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user)
):
    """Update note and automatically re-link entities"""
    updated_note = note_service.update_note(db, note_id, note, current_user.id)
    if not updated_note:
        raise HTTPException(status_code=404, detail="Note not found")
    return updated_note


@router.delete("/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_note(
    note_id: int,
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user)
):
    """Soft delete a note"""
    note = note_service.get_note(db, note_id, current_user.id)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    
    # Soft delete
    db_note = db.query(Notes).filter(
        Notes.id == note_id,
        Notes.owner_id == current_user.id
    ).first()
    db_note.is_deleted = True
    db.commit()