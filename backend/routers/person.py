from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from database.core import get_db
from dependencies import get_current_user
from database.models import Users, Persons
from schemas import PersonResponse, PersonCreate, Note
from services import note_service

router = APIRouter(prefix="/person", tags=["Person"])

@router.get("/", response_model=List[PersonResponse])
def get_persons(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user)
):
    """Get all persons for current user"""
    persons = db.query(Persons).filter(
        Persons.user_id == current_user.id
    ).offset(skip).limit(limit).all()
    return persons


@router.get("/{person_id}", response_model=PersonResponse)
def get_person(
    person_id: int,
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user)
):
    """Get a specific person"""
    person = db.query(Persons).filter(
        Persons.id == person_id,
        Persons.user_id == current_user.id
    ).first()
    
    if not person:
        raise HTTPException(status_code=404, detail="Person not found")
    return person


@router.get("/{person_id}/notes", response_model=List[Note])
def get_person_notes(
    person_id: int,
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user)
):
    """Get all notes that mention this person"""
    return note_service.get_notes_mentioning_person(db, person_id, current_user.id)


@router.post("/", response_model=PersonResponse, status_code=status.HTTP_201_CREATED)
def create_person(
    person: PersonCreate,
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user)
):
    """Create a new person"""
    db_person = Persons(
        user_id=current_user.id,
        **person.dict()
    )
    db.add(db_person)
    db.commit()
    db.refresh(db_person)
    return db_person


@router.put("/{person_id}", response_model=PersonResponse)
def update_person(
    person_id: int,
    person: PersonCreate,
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user)
):
    """Update person details"""
    db_person = db.query(Persons).filter(
        Persons.id == person_id,
        Persons.user_id == current_user.id
    ).first()
    
    if not db_person:
        raise HTTPException(status_code=404, detail="Person not found")
    
    for key, value in person.dict(exclude_unset=True).items():
        setattr(db_person, key, value)
    
    db.commit()
    db.refresh(db_person)
    return db_person