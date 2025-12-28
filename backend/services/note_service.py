from sqlalchemy.orm import Session
from typing import List, Optional
import re
from database import models
from schemas import Note, NoteCreate, Mention, AllMentions
from datetime import datetime

def _extract_places(content: str) -> List[Mention]:
    """Extract place mentions from content
    Patterns: @pl.office, @n.pl.home (n. means new)
    """
    if not content:
        return []
    
    places = re.findall(r'(@(n\.)?pl\.(\w+))', content)
    places = set(places)
    
    return [
        Mention(
            slug=f"@pl.{place[2]}",  # Normalize to @pl.name
            type='place',
            new=(place[1] == "n.")
        ) 
        for place in places
    ]

def _extract_persons(content: str) -> List[Mention]:
    """Extract person mentions from content
    Patterns: @p.john, @n.p.sarah (n. means new)
    """
    if not content:
        return []
    
    persons = re.findall(r'(@(n\.)?p\.(\w+))', content)
    persons = set(persons)
    
    return [
        Mention(
            slug=f"@p.{person[2]}",  # Normalize to @p.name
            type='person',
            new=(person[1] == "n.")
        ) 
        for person in persons
    ]

def _extract_events(content: str) -> List[Mention]:
    """Extract event mentions from content
    Patterns: @e.meeting, @n.e.birthday (n. means new)
    """
    if not content:
        return []
    
    events = re.findall(r'(@(n\.)?e\.(\w+))', content)
    events = set(events)
    
    return [
        Mention(
            slug=f"@e.{event[2]}",  # Normalize to @e.name
            type='event',
            new=(event[1] == "n.")
        ) 
        for event in events
    ]

def parse_note(db_note) -> Note | None:
    """Convert database note to schema with parsed mentions"""
    if not db_note:
        return None
    
    persons: List[Mention] = _extract_persons(db_note.content)
    places: List[Mention] = _extract_places(db_note.content)
    events: List[Mention] = _extract_events(db_note.content)
    
    return Note(
        id=db_note.id,
        title=db_note.title,
        content=db_note.content,
        mentions=AllMentions(places=places, persons=persons, events=events),
        is_pinned=db_note.is_pinned,
        created_at=db_note.created_at,
        updated_at=db_note.updated_at
    )


def _get_or_create_person(db: Session, slug: str, owner_id: int) -> Optional[models.Persons]:
    """Get existing person or create placeholder for new mention"""
    # Remove @n. or @p. prefix to get clean slug
    clean_slug = slug.replace("@n.p.", "").replace("@p.", "")
    
    # Try to find existing person by slug
    person = db.query(models.Persons).filter(
        models.Persons.slug == f"@p.{clean_slug}",
        models.Persons.user_id == owner_id
    ).first()
    
    if not person:
        # Create placeholder person
        person = models.Persons(
            user_id=owner_id,
            slug=f"@p.{clean_slug}",
            first_name=clean_slug.replace("_", " ").title(),  # Convert slug to readable name
            # Other fields can be filled in later by user
        )
        db.add(person)
        db.flush()  # Get the ID without committing
    
    return person


def _get_or_create_place(db: Session, slug: str, owner_id: int) -> Optional[models.Places]:
    """Get existing place or create placeholder for new mention"""
    clean_slug = slug.replace("@n.pl.", "").replace("@pl.", "")
    
    place = db.query(models.Places).filter(
        models.Places.slug == f"@pl.{clean_slug}",
        models.Places.user_id == owner_id
    ).first()
    
    if not place:
        place = models.Places(
            user_id=owner_id,
            slug=f"@pl.{clean_slug}",
            name=clean_slug.replace("_", " ").title(),
        )
        db.add(place)
        db.flush()
    
    return place


def _get_or_create_event(db: Session, slug: str, owner_id: int) -> Optional[models.Events]:
    """Get existing event or create placeholder for new mention"""
    clean_slug = slug.replace("@n.e.", "").replace("@e.", "")
    
    event = db.query(models.Events).filter(
        models.Events.slug == f"@e.{clean_slug}",
        models.Events.user_id == owner_id
    ).first()
    
    if not event:
        # Need a start_datetime for event (required field)
        event = models.Events(
            user_id=owner_id,
            slug=f"@e.{clean_slug}",
            title=clean_slug.replace("_", " ").title(),
            start_datetime=datetime.utcnow(),  # Placeholder
        )
        db.add(event)
        db.flush()
    
    return event


def _link_entities_to_note(db: Session, note: models.Notes, mentions: AllMentions, owner_id: int):
    """
    Link persons, places, and events to the note
    Creates new entities if they don't exist
    """
    # Clear existing relationships
    note.mentioned_persons.clear()
    note.mentioned_places.clear()
    note.mentioned_events.clear()
    
    # Link persons
    for person_mention in mentions.persons:
        person = _get_or_create_person(db, person_mention.slug, owner_id)
        if person:
            note.mentioned_persons.append(person)
    
    # Link places
    for place_mention in mentions.places:
        place = _get_or_create_place(db, place_mention.slug, owner_id)
        if place:
            note.mentioned_places.append(place)
    
    # Link events
    for event_mention in mentions.events:
        event = _get_or_create_event(db, event_mention.slug, owner_id)
        if event:
            note.mentioned_events.append(event)


def create_note(db: Session, note: NoteCreate, owner_id: int):
    """Create a new note and link mentioned entities"""
    try:
        # Import here to avoid circular imports
        from services.relation_service import extract_facts_from_note
        from services.fact_parser import parse_and_store_facts
        
        # Parse #bf...#ef blocks and create facts FIRST
        # This modifies the content to replace #bf...#ef with @f.{id}
        modified_content = parse_and_store_facts(note.content or "", 0, db, owner_id)
        
        # Create note with modified content
        db_note = models.Notes(
            title=note.title,
            content=modified_content,  # Use modified content with @f.{id} references
            is_pinned=note.is_pinned,
            owner_id=owner_id
        )
        db.add(db_note)
        db.flush()  # Get note ID
        
        # Update note_id in NoteFact entries (they were created with note_id=0)
        # Actually, let's fix this by passing the note first
        # Re-parse with actual note_id
        db_note.content = parse_and_store_facts(note.content or "", db_note.id, db, owner_id)
        
        # Extract mentions from modified content
        persons = _extract_persons(db_note.content)
        places = _extract_places(db_note.content)
        events = _extract_events(db_note.content)
        mentions = AllMentions(persons=persons, places=places, events=events)
        
        # Link entities to note
        _link_entities_to_note(db, db_note, mentions, owner_id)
        
        # Extract facts from co-mentions (old automatic extraction)
        extract_facts_from_note(db, db_note, owner_id)
        
        db.commit()
        db.refresh(db_note)
        
        return parse_note(db_note)
    except Exception as e:
        db.rollback()
        raise e


def update_note(db: Session, note_id: int, note: NoteCreate, owner_id: int):
    """Update note and re-link entities based on new content"""
    try:
        # Import here to avoid circular imports
        from services.relation_service import extract_facts_from_note
        from services.fact_parser import parse_and_store_facts
        
        db_note = db.query(models.Notes).filter(
            models.Notes.id == note_id,
            models.Notes.owner_id == owner_id
        ).first()
        
        if not db_note:
            return None
        
        # Update fields
        if note.title is not None:
            db_note.title = note.title
        if note.content is not None:
            # Parse #bf...#ef blocks and create facts
            modified_content = parse_and_store_facts(note.content, note_id, db, owner_id)
            db_note.content = modified_content
            
            # Re-extract and link entities from modified content
            persons = _extract_persons(modified_content)
            places = _extract_places(modified_content)
            events = _extract_events(modified_content)
            mentions = AllMentions(persons=persons, places=places, events=events)
            _link_entities_to_note(db, db_note, mentions, owner_id)
            
            # Re-extract facts from updated note (co-mentions)
            extract_facts_from_note(db, db_note, owner_id)
        
        if note.is_pinned is not None:
            db_note.is_pinned = note.is_pinned
        
        db_note.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(db_note)
        
        return parse_note(db_note)
    except Exception as e:
        db.rollback()
        raise e


def get_note(db: Session, note_id: int, owner_id: Optional[int] = None):
    """Get a single note by ID with all linked entities"""
    query = db.query(models.Notes).filter(models.Notes.id == note_id)
    if owner_id:
        query = query.filter(models.Notes.owner_id == owner_id)
    db_note = query.first()
    return parse_note(db_note)


def get_notes(db: Session, owner_id: int, skip: int = 0, limit: int = 100):
    """Get all notes for a user"""
    notes = db.query(models.Notes).filter(
        models.Notes.owner_id == owner_id,
        models.Notes.is_deleted == False
    ).order_by(
        models.Notes.is_pinned.desc(),
        models.Notes.updated_at.desc()
    ).offset(skip).limit(limit).all()
    
    return [parse_note(note) for note in notes]


def get_notes_mentioning_person(db: Session, person_id: int, owner_id: int):
    """Get all notes that mention a specific person"""
    person = db.query(models.Persons).filter(
        models.Persons.id == person_id,
        models.Persons.user_id == owner_id
    ).first()
    
    if not person:
        return []
    
    # Use the backref to get notes
    return [parse_note(note) for note in person.mentioned_in_notes]


def get_notes_mentioning_place(db: Session, place_id: int, owner_id: int):
    """Get all notes that mention a specific place"""
    place = db.query(models.Places).filter(
        models.Places.id == place_id,
        models.Places.user_id == owner_id
    ).first()
    
    if not place:
        return []
    
    return [parse_note(note) for note in place.mentioned_in_notes]


def get_notes_mentioning_event(db: Session, event_id: int, owner_id: int):
    """Get all notes that mention a specific event"""
    event = db.query(models.Events).filter(
        models.Events.id == event_id,
        models.Events.user_id == owner_id
    ).first()
    
    if not event:
        return []
    
    return [parse_note(note) for note in event.mentioned_in_notes]
