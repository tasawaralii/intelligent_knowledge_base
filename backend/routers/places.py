from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from database.core import get_db
from dependencies import get_current_user
from database.models import Users, Places
from schemas import PlaceResponse, PlaceCreate, Note
from services import note_service

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


@router.get("/{place_id}", response_model=PlaceResponse)
def get_place(
    place_id: int,
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user)
):
    """Get a specific place"""
    place = db.query(Places).filter(
        Places.id == place_id,
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
    db_place = Places(
        user_id=current_user.id,
        **place.dict()
    )
    db.add(db_place)
    db.commit()
    db.refresh(db_place)
    return db_place


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
    
    for key, value in place.dict(exclude_unset=True).items():
        setattr(db_place, key, value)
    
    db.commit()
    db.refresh(db_place)
    return db_place


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