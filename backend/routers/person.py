from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from typing import List, Optional, Type
from database.core import get_db
from dependencies import get_current_user
from database.models import Users, Persons, PersonRelation
from schemas import PersonResponse, PersonCreate, Note, FamilyTree, PersonRelationCreate, PersonRelationRead
from services import note_service
from database import persons as persons_db
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


@router.get("/{person_slug}", response_model=PersonResponse)
def get_person(
    person_slug: str,
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user)
):
    """Get a specific person"""
    person = db.query(Persons).filter(
        Persons.slug == person_slug,
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
    slug_source = person.slug or person.first_name
    slug_value = generate_unique_slug(db, Persons, slug_source)

    db_person = Persons(
        user_id=current_user.id,
        **person.dict(exclude={"slug"}),
        slug=slug_value
    )

    try:
        db.add(db_person)
        db.commit()
        db.refresh(db_person)
        return db_person
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Person slug already exists")


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
    
    payload = person.dict(exclude_unset=True)

    if "slug" in payload:
        new_slug_source = payload.get("slug") or db_person.slug or db_person.first_name
        payload["slug"] = generate_unique_slug(db, Persons, new_slug_source, exclude_id=person_id)

    for key, value in payload.items():
        setattr(db_person, key, value)
    
    if not db_person.slug:
        db_person.slug = generate_unique_slug(db, Persons, db_person.first_name or "person", exclude_id=person_id)
    
    try:
        db.commit()
        db.refresh(db_person)
        return db_person
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Person slug already exists")


@router.get("/{person_id}/family-tree", response_model=FamilyTree)
def get_person_family_tree(
    person_id: int,
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user)
):
    """Get family tree for a person"""
    family_tree = persons_db.get_family_tree(current_user.id, person_id, db)
    
    if not family_tree:
        raise HTTPException(status_code=404, detail="Person not found")
    
    return family_tree


@router.delete("/{person_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_person_endpoint(
    person_id: int,
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user)
):
    """Delete a person"""
    try:
        db_person = db.get(Persons,person_id)
        
        if not db_person:
            raise HTTPException(status_code=404, detail="Person not found")
    
        db.delete(db_person)
        db.commit()
        return {"status":"success", "message":"Person Deleted"}
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(409,"Cannot Delete Person as it is refferenced")


# ==================== Relations Endpoints ====================

# Mapping of relation types to their inverse
INVERSE_RELATIONS = {
    "father": "child",
    "mother": "child",
    "child": None,  # Special: need to know parent's gender
    "spouse": "spouse",
    "sibling": "sibling",
}

def _get_inverse_relation(relation_type: str, related_person: Persons) -> Optional[str]:
    """Get the inverse relation type based on original relation and related person's gender"""
    if relation_type == "child":
        # If I add "child" pointing to someone, the inverse is that person sees me as parent
        # We need the gender of the person_id (not related_person) but we don't have it here
        # So we'll handle this differently - child relations create father/mother based on original person's gender
        return None  # Handled separately
    return INVERSE_RELATIONS.get(relation_type)


@router.post("/{person_id}/relations", response_model=PersonRelationRead, status_code=status.HTTP_201_CREATED)
def create_relation(
    person_id: int,
    relation: PersonRelationCreate,
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user)
):
    """
    Create a relation between two persons with automatic inverse relation.
    
    Examples:
    - Add "father" from A to B: A's father is B → also creates B's child is A
    - Add "child" from A to B: A's child is B → also creates B's father/mother is A (based on A's gender)
    - Add "spouse" from A to B: A's spouse is B → also creates B's spouse is A
    - Add "sibling" from A to B: A's sibling is B → also creates B's sibling is A
    """
    # Verify both persons exist and belong to current user
    person = db.query(Persons).filter(
        Persons.id == person_id,
        Persons.user_id == current_user.id
    ).first()
    
    related = db.query(Persons).filter(
        Persons.id == relation.related_person_id,
        Persons.user_id == current_user.id
    ).first()
    
    if not person or not related:
        raise HTTPException(status_code=404, detail="One or both persons not found")
    
    if person_id == relation.related_person_id:
        raise HTTPException(status_code=400, detail="Cannot create relation with self")
    
    # Check if relation already exists
    existing = db.query(PersonRelation).filter(
        PersonRelation.person_id == person_id,
        PersonRelation.related_person_id == relation.related_person_id,
        PersonRelation.relation_type == relation.relation_type,
        PersonRelation.user_id == current_user.id
    ).first()
    
    if existing:
        raise HTTPException(status_code=409, detail="Relation already exists")
    
    # Create the primary relation
    db_relation = PersonRelation(
        user_id=current_user.id,
        person_id=person_id,
        related_person_id=relation.related_person_id,
        relation_type=relation.relation_type
    )
    db.add(db_relation)
    
    # Create inverse relation
    inverse_type = None
    if relation.relation_type in ["father", "mother"]:
        # A's father/mother is B → B's child is A
        inverse_type = "child"
    elif relation.relation_type == "child":
        # A's child is B → B's father/mother is A (based on A's gender)
        if person.gender and person.gender.lower() in ["male", "m"]:
            inverse_type = "father"
        elif person.gender and person.gender.lower() in ["female", "f"]:
            inverse_type = "mother"
        else:
            # Default to father if gender unknown
            inverse_type = "father"
    elif relation.relation_type == "spouse":
        inverse_type = "spouse"
    elif relation.relation_type == "sibling":
        inverse_type = "sibling"
    
    if inverse_type:
        # Check if inverse already exists
        existing_inverse = db.query(PersonRelation).filter(
            PersonRelation.person_id == relation.related_person_id,
            PersonRelation.related_person_id == person_id,
            PersonRelation.relation_type == inverse_type,
            PersonRelation.user_id == current_user.id
        ).first()
        
        if not existing_inverse:
            inverse_relation = PersonRelation(
                user_id=current_user.id,
                person_id=relation.related_person_id,
                related_person_id=person_id,
                relation_type=inverse_type
            )
            db.add(inverse_relation)
    
    db.commit()
    db.refresh(db_relation)
    return db_relation


@router.get("/{person_id}/relations", response_model=List[PersonRelationRead])
def get_person_relations(
    person_id: int,
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user)
):
    """Get all relations for a person"""
    person = db.query(Persons).filter(
        Persons.id == person_id,
        Persons.user_id == current_user.id
    ).first()
    
    if not person:
        raise HTTPException(status_code=404, detail="Person not found")
    
    relations = db.query(PersonRelation).filter(
        (PersonRelation.person_id == person_id) | (PersonRelation.related_person_id == person_id),
        PersonRelation.user_id == current_user.id
    ).all()
    
    return relations


@router.delete("/{person_id}/relations/{relation_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_relation(
    person_id: int,
    relation_id: int,
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user)
):
    """Delete a relation and its inverse"""
    relation = db.query(PersonRelation).filter(
        PersonRelation.id == relation_id,
        PersonRelation.user_id == current_user.id
    ).first()
    
    if not relation:
        raise HTTPException(status_code=404, detail="Relation not found")
    
    # Determine inverse relation type
    inverse_type = None
    if relation.relation_type in ["father", "mother"]:
        inverse_type = "child"
    elif relation.relation_type == "child":
        # Find what type the inverse might be (father or mother)
        inverse_types = ["father", "mother"]
        for inv_type in inverse_types:
            existing = db.query(PersonRelation).filter(
                PersonRelation.person_id == relation.related_person_id,
                PersonRelation.related_person_id == relation.person_id,
                PersonRelation.relation_type == inv_type,
                PersonRelation.user_id == current_user.id
            ).first()
            if existing:
                db.delete(existing)
                break
    elif relation.relation_type in ["spouse", "sibling"]:
        inverse_type = relation.relation_type
    
    # Delete inverse if found
    if inverse_type:
        inverse = db.query(PersonRelation).filter(
            PersonRelation.person_id == relation.related_person_id,
            PersonRelation.related_person_id == relation.person_id,
            PersonRelation.relation_type == inverse_type,
            PersonRelation.user_id == current_user.id
        ).first()
        if inverse:
            db.delete(inverse)
    
    db.delete(relation)
    db.commit()
    return {"status": "success", "message": "Relation deleted"}