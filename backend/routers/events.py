from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from database.core import get_db
from dependencies import get_current_user
from database.models import Users, Events
from schemas import EventResponse, EventCreate, Note
from services import note_service

router = APIRouter(prefix="/event", tags=["Event"])

@router.get("/", response_model=List[EventResponse])
def get_events(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user)
):
    """Get all events for current user"""
    events = db.query(Events).filter(
        Events.user_id == current_user.id
    ).order_by(Events.start_datetime.desc()).offset(skip).limit(limit).all()
    return events


@router.get("/{event_id}", response_model=EventResponse)
def get_event(
    event_id: int,
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user)
):
    """Get a specific event"""
    event = db.query(Events).filter(
        Events.id == event_id,
        Events.user_id == current_user.id
    ).first()
    
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return event


@router.get("/{event_id}/notes", response_model=List[Note])
def get_event_notes(
    event_id: int,
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user)
):
    """Get all notes that mention this event"""
    return note_service.get_notes_mentioning_event(db, event_id, current_user.id)


@router.post("/", response_model=EventResponse, status_code=status.HTTP_201_CREATED)
def create_event(
    event: EventCreate,
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user)
):
    """Create a new event"""
    db_event = Events(
        user_id=current_user.id,
        **event.dict()
    )
    db.add(db_event)
    db.commit()
    db.refresh(db_event)
    return db_event


@router.put("/{event_id}", response_model=EventResponse)
def update_event(
    event_id: int,
    event: EventCreate,
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user)
):
    """Update event details"""
    db_event = db.query(Events).filter(
        Events.id == event_id,
        Events.user_id == current_user.id
    ).first()
    
    if not db_event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    for key, value in event.dict(exclude_unset=True).items():
        setattr(db_event, key, value)
    
    db.commit()
    db.refresh(db_event)
    return db_event


@router.delete("/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_event(
    event_id: int,
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user)
):
    """Delete an event"""
    db_event = db.query(Events).filter(
        Events.id == event_id,
        Events.user_id == current_user.id
    ).first()
    
    if not db_event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    db.delete(db_event)
    db.commit()
    return None
