from sqlalchemy.orm import Session
from typing import Optional, List
import database.models as models
from schemas import EntityCreate, EntityRelationshipCreate, Entity, EntityRelationship, ConnectionPath, RelatedNotesCluster
import re
from collections import defaultdict, deque


def extract_entities(text: str, entity_type: str = None) -> dict:
    """
    Extract entities from text using pattern matching
    Returns dict with entity_type as key and list of entities as value
    """
    entities = defaultdict(set)
    
    if not text:
        return entities
    
    # Extract dates (simplified patterns)
    date_patterns = [
        r'\d{1,2}/\d{1,2}/\d{4}',  # MM/DD/YYYY
        r'\d{1,2}-\d{1,2}-\d{4}',  # MM-DD-YYYY
        r'(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4}',
        r'(Mon|Tue|Wed|Thu|Fri|Sat|Sun)\w*',
    ]
    for pattern in date_patterns:
        entities['date'].update(re.findall(pattern, text, re.IGNORECASE))
    
    # Extract emails as people/concepts
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    entities['person'].update(re.findall(email_pattern, text))
    
    # Extract @mentions as people
    mention_pattern = r'@(\w+)'
    entities['person'].update(re.findall(mention_pattern, text))
    
    # Extract hashtags as topics
    hashtag_pattern = r'#(\w+)'
    entities['topic'].update(re.findall(hashtag_pattern, text))
    
    # Extract capitalized phrases as concepts/places (simplified)
    capitalized_pattern = r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b'
    potential_proper_nouns = set(re.findall(capitalized_pattern, text))
    for noun in potential_proper_nouns:
        if len(noun) > 2 and noun not in ['The', 'And', 'But', 'For']:
            entities['concept'].add(noun)
    
    return dict(entities)


def create_entity(db: Session, entity: EntityCreate, owner_id: int) -> Entity:
    """Create a new entity"""
    db_entity = models.Entity(
        name=entity.name,
        entity_type=entity.entity_type,
        description=entity.description,
        owner_id=owner_id
    )
    db.add(db_entity)
    db.commit()
    db.refresh(db_entity)
    return db_entity


def get_or_create_entity(db: Session, name: str, entity_type: str, owner_id: int) -> models.Entity:
    """Get existing entity or create if not exists"""
    entity = db.query(models.Entity).filter(
        models.Entity.name == name,
        models.Entity.entity_type == entity_type,
        models.Entity.owner_id == owner_id
    ).first()
    
    if not entity:
        entity = models.Entity(
            name=name,
            entity_type=entity_type,
            owner_id=owner_id
        )
        db.add(entity)
        db.commit()
        db.refresh(entity)
    
    return entity


def extract_entities_from_note(db: Session, note_id: int, owner_id: int, content: str, title: str):
    """Extract all entities from note and link them"""
    entities_dict = extract_entities(content)
    entities_dict.update(extract_entities(title))
    
    db_note = db.query(models.Notes).filter(
        models.Notes.id == note_id,
        models.Notes.owner_id == owner_id
    ).first()
    
    if not db_note:
        return []
    
    extracted_entities = []
    for entity_type, entity_names in entities_dict.items():
        for entity_name in entity_names:
            db_entity = get_or_create_entity(db, entity_name, entity_type, owner_id)
            
            # Link note to entity if not already linked
            if db_entity not in db_note.entities:
                db_note.entities.append(db_entity)
            
            extracted_entities.append(db_entity)
    
    db.commit()
    return extracted_entities


def create_entity_relationship(db: Session, relationship: EntityRelationshipCreate, owner_id: int) -> EntityRelationship:
    """Create relationship between two entities"""
    db_relationship = models.EntityRelationship(
        from_entity_id=relationship.from_entity_id,
        to_entity_id=relationship.to_entity_id,
        relationship_type=relationship.relationship_type,
        owner_id=owner_id
    )
    db.add(db_relationship)
    db.commit()
    db.refresh(db_relationship)
    return db_relationship


def auto_create_relationships(db: Session, note_id: int, owner_id: int):
    """Automatically create relationships between entities that appear together in notes"""
    note = db.query(models.Notes).filter(
        models.Notes.id == note_id,
        models.Notes.owner_id == owner_id
    ).first()
    
    if not note or not note.entities:
        return
    
    # Create relationships between all entity pairs in the note
    entities = note.entities
    for i, entity1 in enumerate(entities):
        for entity2 in entities[i+1:]:
            # Check if relationship already exists
            existing = db.query(models.EntityRelationship).filter(
                models.EntityRelationship.from_entity_id == entity1.id,
                models.EntityRelationship.to_entity_id == entity2.id,
                models.EntityRelationship.owner_id == owner_id
            ).first()
            
            if existing:
                # Increase strength if already exists
                existing.strength += 1
            else:
                # Create new relationship
                relationship = models.EntityRelationship(
                    from_entity_id=entity1.id,
                    to_entity_id=entity2.id,
                    relationship_type='mentioned_with',
                    strength=1,
                    owner_id=owner_id
                )
                db.add(relationship)
    
    db.commit()


def find_connection_path(db: Session, from_entity_id: int, to_entity_id: int, owner_id: int, max_depth: int = 3) -> Optional[ConnectionPath]:
    """Find shortest path between two entities using BFS"""
    from_entity = db.query(models.Entity).filter(
        models.Entity.id == from_entity_id,
        models.Entity.owner_id == owner_id
    ).first()
    
    to_entity = db.query(models.Entity).filter(
        models.Entity.id == to_entity_id,
        models.Entity.owner_id == owner_id
    ).first()
    
    if not from_entity or not to_entity:
        return None
    
    # BFS to find shortest path
    queue = deque([(from_entity.id, [from_entity.id], [])])
    visited = {from_entity.id}
    
    while queue:
        current_id, path, relationship_chain = queue.popleft()
        
        if len(path) - 1 > max_depth:
            continue
        
        if current_id == to_entity_id:
            # Reconstruct path with entity objects
            path_entities = []
            for entity_id in path:
                entity = db.query(models.Entity).filter(models.Entity.id == entity_id).first()
                if entity:
                    path_entities.append(entity)
            
            return ConnectionPath(
                start_entity=from_entity,
                end_entity=to_entity,
                path=path_entities,
                relationship_chain=relationship_chain,
                total_distance=len(path) - 1
            )
        
        # Get all connected entities
        relationships = db.query(models.EntityRelationship).filter(
            models.EntityRelationship.from_entity_id == current_id,
            models.EntityRelationship.owner_id == owner_id
        ).all()
        
        for rel in relationships:
            next_id = rel.to_entity_id
            if next_id not in visited:
                visited.add(next_id)
                queue.append((
                    next_id,
                    path + [next_id],
                    relationship_chain + [rel.relationship_type]
                ))
    
    return None


def get_related_notes_clusters(db: Session, owner_id: int, min_shared_entities: int = 2) -> List[RelatedNotesCluster]:
    """Find clusters of related notes based on shared entities"""
    # Get all notes for user
    notes = db.query(models.Notes).filter(
        models.Notes.owner_id == owner_id
    ).all()
    
    if len(notes) < 2:
        return []
    
    clusters = []
    processed_notes = set()
    
    for i, note1 in enumerate(notes):
        if note1.id in processed_notes:
            continue
        
        cluster_notes = {note1.id}
        cluster_entities = set(entity.id for entity in note1.entities)
        
        for note2 in notes[i+1:]:
            if note2.id in processed_notes:
                continue
            
            note2_entities = set(entity.id for entity in note2.entities)
            shared_entities = cluster_entities.intersection(note2_entities)
            
            if len(shared_entities) >= min_shared_entities:
                cluster_notes.add(note2.id)
                cluster_entities.update(note2_entities)
        
        if len(cluster_notes) > 1:
            relevance_score = len(cluster_entities) / max(len(cluster_notes), 1)
            clusters.append(RelatedNotesCluster(
                entity_ids=list(cluster_entities),
                note_ids=list(cluster_notes),
                shared_entity_count=len(cluster_entities),
                relevance_score=relevance_score
            ))
            processed_notes.update(cluster_notes)
    
    return clusters


def search_entities_by_type(db: Session, entity_type: str, owner_id: int) -> List[Entity]:
    """Search entities by type"""
    entities = db.query(models.Entity).filter(
        models.Entity.entity_type == entity_type,
        models.Entity.owner_id == owner_id
    ).all()
    return entities


def get_entity_connections(db: Session, entity_id: int, owner_id: int) -> dict:
    """Get all connections for an entity"""
    entity = db.query(models.Entity).filter(
        models.Entity.id == entity_id,
        models.Entity.owner_id == owner_id
    ).first()
    
    if not entity:
        return None
    
    outgoing = db.query(models.EntityRelationship).filter(
        models.EntityRelationship.from_entity_id == entity_id,
        models.EntityRelationship.owner_id == owner_id
    ).all()
    
    incoming = db.query(models.EntityRelationship).filter(
        models.EntityRelationship.to_entity_id == entity_id,
        models.EntityRelationship.owner_id == owner_id
    ).all()
    
    return {
        "entity": entity,
        "outgoing_relationships": outgoing,
        "incoming_relationships": incoming
    }
