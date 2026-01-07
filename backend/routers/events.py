from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from typing import List, Optional, Type
from database.core import get_db
from dependencies import get_current_user
from database.models import Users, Events
from schemas import EventResponse, EventCreate, Note
from services import note_service
from slugify import slugify


def generate_unique_slug(db: Session, model: Type, base_value: str, exclude_id: Optional[int] = None) -> str:
    """Generate a unique slug for a model by appending a counter when needed."""
    base_slug = slugify(base_value or "")
    if not base_slug:
        raise HTTPException(status_code=400, detail="Slug cannot be empty")

    candidate = base_slug
    counter = 2
    while True:
        query = db.query(model).filter(model.slug == candidate)
        if exclude_id:
            query = query.filter(model.id != exclude_id)
        if not db.query(query.exists()).scalar():
            return candidate
        candidate = f"{base_slug}-{counter}"
        counter += 1

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


@router.get("/{event_slug}", response_model=EventResponse)
def get_event(
    event_slug: str,
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user)
):
    """Get a specific event"""
    event = db.query(Events).filter(
        Events.slug == event_slug,
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
    slug_source = event.slug or event.title
    slug_value = generate_unique_slug(db, Events, slug_source)

    db_event = Events(
        user_id=current_user.id,
        **event.dict(exclude={"slug"}),
        slug=slug_value
    )

    try:
        db.add(db_event)
        db.commit()
        db.refresh(db_event)
        return db_event
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Event slug already exists")


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
    
    payload = event.dict(exclude_unset=True)

    if "slug" in payload:
        new_slug_source = payload.get("slug") or db_event.slug or db_event.title
        payload["slug"] = generate_unique_slug(db, Events, new_slug_source, exclude_id=event_id)

    for key, value in payload.items():
        setattr(db_event, key, value)
    
    if not db_event.slug:
        db_event.slug = generate_unique_slug(db, Events, db_event.title or "event", exclude_id=event_id)
    
    try:
        db.commit()
        db.refresh(db_event)
        return db_event
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Event slug already exists")


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
