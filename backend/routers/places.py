from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from typing import List, Optional, Type
from database.core import get_db
from dependencies import get_current_user
from database.models import Users, Places
from schemas import PlaceResponse, PlaceCreate, Note
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

router = APIRouter(prefix="/place", tags=["Place"])

@router.get("/", response_model=List[PlaceResponse])
def get_places(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user)
):
    """Get all places for current user"""
    places = db.query(Places).filter(
        Places.user_id == current_user.id
    ).offset(skip).limit(limit).all()
    return places


@router.get("/{place_slug}", response_model=PlaceResponse)
def get_place(
    place_slug: str,
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user)
):
    """Get a specific place"""
    place = db.query(Places).filter(
        Places.slug == place_slug,
        Places.user_id == current_user.id
    ).first()
    
    if not place:
        raise HTTPException(status_code=404, detail="Place not found")
    return place


@router.get("/{place_id}/notes", response_model=List[Note])
def get_place_notes(
    place_id: int,
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user)
):
    """Get all notes that mention this place"""
    return note_service.get_notes_mentioning_place(db, place_id, current_user.id)


@router.post("/", response_model=PlaceResponse, status_code=status.HTTP_201_CREATED)
def create_place(
    place: PlaceCreate,
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user)
):
    """Create a new place"""
    slug_source = place.slug or place.name
    slug_value = generate_unique_slug(db, Places, slug_source)

    db_place = Places(
        user_id=current_user.id,
        **place.dict(exclude={"slug"}),
        slug=slug_value
    )

    try:
        db.add(db_place)
        db.commit()
        db.refresh(db_place)
        return db_place
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Place slug already exists")


@router.put("/{place_id}", response_model=PlaceResponse)
def update_place(
    place_id: int,
    place: PlaceCreate,
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user)
):
    """Update place details"""
    db_place = db.query(Places).filter(
        Places.id == place_id,
        Places.user_id == current_user.id
    ).first()
    
    if not db_place:
        raise HTTPException(status_code=404, detail="Place not found")
    
    payload = place.dict(exclude_unset=True)

    if "slug" in payload:
        new_slug_source = payload.get("slug") or db_place.slug or db_place.name
        payload["slug"] = generate_unique_slug(db, Places, new_slug_source, exclude_id=place_id)

    for key, value in payload.items():
        setattr(db_place, key, value)
    
    if not db_place.slug:
        db_place.slug = generate_unique_slug(db, Places, db_place.name or "place", exclude_id=place_id)
    
    try:
        db.commit()
        db.refresh(db_place)
        return db_place
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Place slug already exists")


@router.delete("/{place_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_place(
    place_id: int,
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user)
):
    """Delete a place"""
    db_place = db.query(Places).filter(
        Places.id == place_id,
        Places.user_id == current_user.id
    ).first()
    
    if not db_place:
        raise HTTPException(status_code=404, detail="Place not found")
    
    db.delete(db_place)
    db.commit()
    return None