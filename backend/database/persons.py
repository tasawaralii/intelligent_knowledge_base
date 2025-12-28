from sqlalchemy.orm import Session
from typing import List, Tuple
from .models import Persons, PersonChanges
from schemas import PersonCreate, PersonRead, PersonUpdate, PersonChange


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