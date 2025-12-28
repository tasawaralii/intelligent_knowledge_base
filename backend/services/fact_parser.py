"""
Fact Parser Service
Parses #bf...#ef blocks from notes and creates structured facts
Replaces fact blocks with @f.{id} references for dynamic rendering
"""

import re
from typing import Tuple, List, Optional
from sqlalchemy.orm import Session
from database import models
from database.facts import Facts, NoteFact, RelationType
from datetime import datetime


def parse_and_store_facts(content: str, note_id: int, db: Session, user_id: int) -> str:
    """
    Parse #bf...#ef blocks, create facts, and replace with @f.{id}
    
    Example input:
        "Today I saw @p.saeed, #bf @p.saeed meets @p.anas #ef at school"
    
    Returns modified content:
        "Today I saw @p.saeed, @f.1 at school"
    
    Args:
        content: Original note content with #bf...#ef blocks
        note_id: ID of the note being processed
        db: Database session
        user_id: Owner of the note
    
    Returns:
        Modified content with @f.{id} replacing #bf...#ef blocks
    """
    if not content:
        return content
    
    # Pattern to match #bf...#ef blocks (case insensitive, allows multiline)
    fact_pattern = r'#bf\s+(.*?)\s+#ef'
    matches = list(re.finditer(fact_pattern, content, re.IGNORECASE | re.DOTALL))
    
    # Process in reverse order to maintain correct positions
    modified_content = content
    offset = 0
    
    for match in matches:
        fact_text = match.group(1).strip()
        original_start = match.start()
        original_end = match.end()
        
        # Create fact from the extracted text
        fact_id = extract_and_create_fact(fact_text, note_id, db, user_id, original_start)
        
        if fact_id:
            # Replace #bf...#ef with @f.{id}
            replacement = f"@f.{fact_id}"
            
            # Calculate adjusted positions
            start = original_start + offset
            end = original_end + offset
            
            modified_content = modified_content[:start] + replacement + modified_content[end:]
            
            # Update offset for next replacement
            offset += len(replacement) - (original_end - original_start)
    
    return modified_content


def extract_and_create_fact(fact_text: str, note_id: int, db: Session, user_id: int, position: int) -> Optional[int]:
    """
    Parse fact text and create a structured fact in database
    
    Supported patterns:
        @p.john meets @p.jane
        @p.sarah studies at @pl.uet
        @p.ali works at @pl.office
        @p.john attends @e.meeting
        @e.conference located at @pl.hotel
    
    Returns:
        fact_id if successful, None if parsing failed
    """
    # Pattern: @{type}.{name} {relation} @{type}.{name}
    # Supports: @p.name, @pl.name, @e.name
    pattern = r'@(p|pl|e)\.(\w+)\s+([a-z_\s]+?)\s+@(p|pl|e)\.(\w+)'
    match = re.match(pattern, fact_text.strip(), re.IGNORECASE)
    
    if not match:
        return None
    
    source_type_abbr, source_name, relation_raw, target_type_abbr, target_name = match.groups()
    
    # Convert abbreviations to full types
    type_map = {'p': 'person', 'pl': 'place', 'e': 'event'}
    source_type = type_map.get(source_type_abbr.lower())
    target_type = type_map.get(target_type_abbr.lower())
    
    if not source_type or not target_type:
        return None
    
    # Clean relation type (remove extra spaces, convert to snake_case)
    relation_type = relation_raw.strip().replace(' ', '_').lower()
    
    # Resolve entities by slug
    source_id = resolve_entity_by_slug(source_type, source_name, user_id, db)
    target_id = resolve_entity_by_slug(target_type, target_name, user_id, db)
    
    if not source_id or not target_id:
        # Entity not found - skip this fact
        return None
    
    # Check if fact already exists
    existing_fact = db.query(Facts).filter(
        Facts.user_id == user_id,
        Facts.source_type == source_type,
        Facts.source_id == source_id,
        Facts.target_type == target_type,
        Facts.target_id == target_id,
        Facts.relation_type == relation_type
    ).first()
    
    if existing_fact:
        # Update confidence and link to note
        db.execute(
            Facts.__table__.update()
            .where(Facts.id == existing_fact.id)
            .values(
                confidence_score=Facts.confidence_score + 5,
                updated_at=datetime.utcnow()
            )
        )
        fact_id = existing_fact.id
    else:
        # Create new fact
        fact = Facts(
            user_id=user_id,
            source_type=source_type,
            source_id=source_id,
            target_type=target_type,
            target_id=target_id,
            relation_type=relation_type,
            confidence_score=10,  # High confidence (user explicitly stated)
            description=fact_text,
            extracted_from_text=fact_text
        )
        db.add(fact)
        db.flush()
        fact_id = fact.id
    
    # Link fact to note
    note_fact = NoteFact(
        note_id=note_id,
        fact_id=fact_id,
        position_in_note=position
    )
    db.add(note_fact)
    db.flush()
    
    return fact_id


def resolve_entity_by_slug(entity_type: str, slug_name: str, user_id: int, db: Session) -> Optional[int]:
    """
    Find entity ID by slug name
    
    Args:
        entity_type: 'person', 'place', or 'event'
        slug_name: Name from @{type}.{slug_name}
        user_id: Owner of entities
        db: Database session
    
    Returns:
        Entity ID if found, None otherwise
    """
    # Create the proper slug format
    prefix_map = {'person': 'p', 'place': 'pl', 'event': 'e', 'p': 'p', 'pl': 'pl', 'e': 'e'}
    prefix = prefix_map.get(entity_type, 'p')
    slug = f"@{prefix}.{slug_name}"
    
    if entity_type == 'person':
        entity = db.query(models.Persons).filter(
            models.Persons.slug == slug,
            models.Persons.user_id == user_id
        ).first()
    elif entity_type == 'place':
        entity = db.query(models.Places).filter(
            models.Places.slug == slug,
            models.Places.user_id == user_id
        ).first()
    elif entity_type == 'event':
        entity = db.query(models.Events).filter(
            models.Events.slug == slug,
            models.Events.user_id == user_id
        ).first()
    else:
        return None
    
    return entity.id if entity else None


def get_fact_details(fact_id: int, user_id: int, db: Session) -> Optional[dict]:
    """
    Get detailed information about a fact for rendering
    
    Returns:
        {
            'id': 1,
            'source': {'type': 'person', 'id': 5, 'name': 'John Doe'},
            'target': {'type': 'place', 'id': 3, 'name': 'UET'},
            'relation_type': 'studies_at',
            'confidence': 10,
            'description': '@p.john studies at @pl.uet',
            'created_at': '2025-12-28T...'
        }
    """
    fact = db.query(Facts).filter(
        Facts.id == fact_id,
        Facts.user_id == user_id
    ).first()
    
    if not fact:
        return None
    
    # Get source entity details (cast to proper types)
    source_entity = _get_entity_details(fact.source_type, fact.source_id, user_id, db)
    target_entity = _get_entity_details(fact.target_type, fact.target_id, user_id, db)
    
    return {
        'id': fact.id,
        'source': source_entity,
        'target': target_entity,
        'relation_type': fact.relation_type,
        'confidence': fact.confidence_score,
        'description': fact.description or fact.extracted_from_text or '',
        'created_at': fact.created_at.isoformat()
    }


def _get_entity_details(entity_type: str, entity_id: int, user_id: int, db: Session) -> Optional[dict]:
    """Helper to get entity name and details"""
    if entity_type == 'person':
        entity = db.query(models.Persons).filter(
            models.Persons.id == entity_id,
            models.Persons.user_id == user_id
        ).first()
        if entity:
            return {
                'type': 'person',
                'id': entity.id,
                'name': f"{entity.first_name} {entity.last_name or ''}".strip()
            }
    elif entity_type == 'place':
        entity = db.query(models.Places).filter(
            models.Places.id == entity_id,
            models.Places.user_id == user_id
        ).first()
        if entity:
            return {
                'type': 'place',
                'id': entity.id,
                'name': entity.name
            }
    elif entity_type == 'event':
        entity = db.query(models.Events).filter(
            models.Events.id == entity_id,
            models.Events.user_id == user_id
        ).first()
        if entity:
            return {
                'type': 'event',
                'id': entity.id,
                'name': entity.title
            }
    
    return None
