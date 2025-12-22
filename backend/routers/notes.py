from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database.core import get_db
from database.notes import create_note, get_note, get_user_notes, get_pinned_notes, delete_note
from database.user import get_user
from routers.auth import oauth2_scheme
from schemas import NoteCreate, Note, Notes
from jose import jwt, JWTError
import os

router = APIRouter(prefix="/notes", tags=["notes"])

SECRET_KEY = str(os.getenv("SECRET_KEY"))
ALGORITHM = str(os.getenv("ALGORITHM"))


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """Get current user from JWT token"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = get_user(username, db)
    if user is None:
        raise credentials_exception
    return user


@router.get("/", response_model=Notes)
async def list_notes(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    """Get all notes for the current user"""
    notes = get_user_notes(db, current_user.id, skip, limit)
    return Notes(notes=notes)


@router.get("/pinned")
async def list_pinned_notes(db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    """Get all pinned notes for the current user"""
    notes = get_pinned_notes(db, current_user.id)
    return Notes(notes=notes)


@router.post("", response_model=Note)
async def create_new_note(note: NoteCreate, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    """Create a new note"""
    db_note = create_note(db, note, current_user.id)
    return db_note


@router.get("/{note_id}", response_model=Note)
async def read_note(note_id: int, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    """Get a specific note by ID"""
    db_note = get_note(db, note_id, current_user.id)
    if not db_note:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found")
    return db_note


@router.delete("/{note_id}")
async def delete_existing_note(note_id: int, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    """Delete a note"""
    db_note = delete_note(db, note_id, current_user.id)
    if not db_note:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found")
    return {"message": "Note deleted successfully"}