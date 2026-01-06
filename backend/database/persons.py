from sqlalchemy.orm import Session
from typing import List, Tuple, Optional
from .models import Persons, PersonChanges
from schemas import PersonCreate, PersonRead, PersonUpdate, PersonChange, FamilyMember, FamilyTreeNode, FamilyTree


def _convert_person(person: Persons) -> PersonRead:
    """Map ORM object to response schema"""
    return PersonRead(
        id=person.id,
        first_name=person.first_name,
        last_name=person.last_name,
        father_name=person.father_name,
        cnic=person.cnic,
        phone_number=person.phone_number,
        email=person.email,
        address=person.address,
        city=person.city,
        country=person.country,
        date_of_birth=person.date_of_birth,
        gender=person.gender,
        picture_url=person.picture_url,
        father_id=person.father_id,
        mother_id=person.mother_id,
        spouse_id=person.spouse_id,
        created_at=person.created_at,
        updated_at=person.updated_at,
    )


def add_person(user_id: int, person: PersonCreate, db: Session) -> PersonRead:
    new_person = Persons(
        user_id=user_id,
        first_name=person.first_name,
        last_name=person.last_name,
        father_name=person.father_name,
        cnic=person.cnic,
        phone_number=person.phone_number,
        email=person.email,
        address=person.address,
        city=person.city,
        country=person.country,
        date_of_birth=person.date_of_birth,
        gender=person.gender,
        picture_url=person.picture_url,
        father_id=person.father_id,
        mother_id=person.mother_id,
        spouse_id=person.spouse_id,
    )

    db.add(new_person)
    db.commit()
    db.refresh(new_person)
    return _convert_person(new_person)


def delete_person(user_id: int, person_id: int, db: Session) -> bool:
    person = db.query(Persons).filter(Persons.id == person_id, Persons.user_id == user_id).first()
    if not person:
        return False

    db.delete(person)
    db.commit()
    return True


def get_persons(user_id: int, page: int, db: Session) -> List[PersonRead]:
    offset = (page - 1) * 10
    persons = (
        db.query(Persons)
        .filter(Persons.user_id == user_id)
        .offset(offset)
        .limit(10)
        .all()
    )
    return [_convert_person(person) for person in persons]


def update_person(user_id: int, person_id: int, updates: PersonUpdate, db: Session) -> Tuple[PersonRead, List[PersonChange]] | Tuple[None, None]:
    person = db.query(Persons).filter(Persons.id == person_id, Persons.user_id == user_id).first()
    if not person:
        return None, None

    change_logs: List[PersonChange] = []

    mutable_fields = [
        "first_name",
        "last_name",
        "father_name",
        "cnic",
        "phone_number",
        "email",
        "address",
        "city",
        "country",
        "date_of_birth",
        "gender",
        "picture_url",
        "father_id",
        "mother_id",
        "spouse_id",
    ]

    for field_name in mutable_fields:
        new_value = getattr(updates, field_name)
        if new_value is None:
            continue
        old_value = getattr(person, field_name)
        if old_value == new_value:
            continue
        setattr(person, field_name, new_value)
        log = PersonChanges(
            person_id=person.id,
            field=field_name,
            old_value=str(old_value) if old_value is not None else None,
            new_value=str(new_value) if new_value is not None else None,
        )
        db.add(log)

    db.commit()
    db.refresh(person)

    # Fetch the logs we just created to return consistent payload
    logs = (
        db.query(PersonChanges)
        .filter(PersonChanges.person_id == person.id)
        .order_by(PersonChanges.changed_at.desc())
        .limit(10)
        .all()
    )
    for log in logs:
        change_logs.append(
            PersonChange(
                field=log.field,
                old_value=log.old_value,
                new_value=log.new_value,
                changed_at=log.changed_at,
            )
        )

    return _convert_person(person), change_logs


def _person_to_family_member(person: Persons) -> FamilyMember:
    # \"\"\"Convert Persons model to FamilyMember schema\"\"\"
    return FamilyMember(
        id=person.id,
        first_name=person.first_name,
        last_name=person.last_name,
        gender=person.gender,
        date_of_birth=person.date_of_birth,
        picture_url=person.picture_url
    )


def get_family_tree(user_id: int, person_id: int, db: Session) -> Optional[FamilyTree]:
    # \"\"\"Get family tree for a person including ancestors and descendants\"\"\"
    root_person = db.query(Persons).filter(
        Persons.id == person_id,
        Persons.user_id == user_id
    ).first()
    
    if not root_person:
        return None
    
    # Collect all family members
    visited = set()
    nodes = []
    max_generations = 0
    
    def process_person(person: Persons, generation: int = 0):
        nonlocal max_generations
        if person.id in visited:
            return
        visited.add(person.id)
        max_generations = max(max_generations, generation)
        
        # Get relationships
        father = db.query(Persons).filter(Persons.id == person.father_id).first() if person.father_id else None
        mother = db.query(Persons).filter(Persons.id == person.mother_id).first() if person.mother_id else None
        spouse = db.query(Persons).filter(Persons.id == person.spouse_id).first() if person.spouse_id else None
        
        # Get children (where this person is father or mother)
        children = db.query(Persons).filter(
            (Persons.father_id == person.id) | (Persons.mother_id == person.id),
            Persons.user_id == user_id
        ).all()
        
        # Get siblings (same parents)
        siblings = []
        if person.father_id or person.mother_id:
            siblings = db.query(Persons).filter(
                ((Persons.father_id == person.father_id) | (Persons.mother_id == person.mother_id)),
                Persons.id != person.id,
                Persons.user_id == user_id
            ).all()
        
        # Create node
        node = FamilyTreeNode(
            person=_person_to_family_member(person),
            father=_person_to_family_member(father) if father else None,
            mother=_person_to_family_member(mother) if mother else None,
            spouse=_person_to_family_member(spouse) if spouse else None,
            children=[_person_to_family_member(child) for child in children],
            siblings=[_person_to_family_member(sibling) for sibling in siblings]
        )
        nodes.append(node)
        
        # Recursively process family members
        if father:
            process_person(father, generation + 1)
        if mother:
            process_person(mother, generation + 1)
        if spouse:
            process_person(spouse, generation)
        for child in children:
            process_person(child, generation - 1)
    
    process_person(root_person)
    
    return FamilyTree(
        root_person=_person_to_family_member(root_person),
        nodes=nodes,
        generations=max_generations + 1
    )