from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database.core import get_db
from database.relationships import (
    extract_entities_from_note, 
    create_entity, 
    create_entity_relationship,
    find_connection_path,
    get_related_notes_clusters,
    search_entities_by_type,
    get_entity_connections,
    auto_create_relationships
)
from database.user import get_user
from routers.auth import oauth2_scheme
from schemas import Entity, EntityCreate, EntityRelationship, EntityRelationshipCreate, ConnectionPath, RelatedNotesCluster
import database.models as models
from jose import jwt, JWTError
import os

router = APIRouter(prefix="/relationships", tags=["relationships"])

SECRET_KEY = str(os.getenv("SECRET_KEY"))
ALGORITHM = str(os.getenv("ALGORITHM"))


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """Get current user from JWT token"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = get_user(username, db)
    if user is None:
        raise credentials_exception
    return user


@router.post("/extract/{note_id}")
async def extract_note_entities(note_id: int, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    """Extract entities from a note and create relationships"""
    from database.notes import get_note
    
    # Get note
    note = get_note(db, note_id, current_user.id)
    if not note:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found")
    
    # Query directly for full note content
    db_note = db.query(models.Notes).filter(
        models.Notes.id == note_id,
        models.Notes.owner_id == current_user.id
    ).first()
    
    if not db_note:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found")
    
    extracted = extract_entities_from_note(db, note_id, current_user.id, db_note.content or "", db_note.title or "")
    
    # Auto-create relationships
    auto_create_relationships(db, note_id, current_user.id)
    
    return {"note_id": note_id, "extracted_entities": len(extracted), "entities": [{"id": e.id, "name": e.name, "type": e.entity_type} for e in extracted]}


@router.post("/entities", response_model=Entity)
async def create_new_entity(entity: EntityCreate, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    """Create a new entity"""
    db_entity = create_entity(db, entity, current_user.id)
    return db_entity


@router.post("/relationships", response_model=EntityRelationship)
async def create_new_relationship(relationship: EntityRelationshipCreate, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    """Create a relationship between two entities"""
    # Verify both entities exist and belong to user
    
    from_entity = db.query(models.Entity).filter(
        models.Entity.id == relationship.from_entity_id,
        models.Entity.owner_id == current_user.id
    ).first()
    
    to_entity = db.query(models.Entity).filter(
        models.Entity.id == relationship.to_entity_id,
        models.Entity.owner_id == current_user.id
    ).first()
    
    if not from_entity or not to_entity:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="One or both entities not found")
    
    db_relationship = create_entity_relationship(db, relationship, current_user.id)
    return db_relationship


@router.get("/entities/by-type/{entity_type}")
async def get_entities_by_type(entity_type: str, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    """Get all entities of a specific type"""
    entities = search_entities_by_type(db, entity_type, current_user.id)
    return {"entity_type": entity_type, "entities": entities}


@router.get("/entities/{entity_id}/connections")
async def get_entity_graph(entity_id: int, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    """Get all connections for an entity"""
    connections = get_entity_connections(db, entity_id, current_user.id)
    if not connections:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Entity not found")
    return connections


@router.get("/path/{from_entity_id}/{to_entity_id}")
async def find_path(from_entity_id: int, to_entity_id: int, max_depth: int = 3, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    """Find connection path between two entities: 'How are X and Y connected?'"""
    path = find_connection_path(db, from_entity_id, to_entity_id, current_user.id, max_depth)
    
    if not path:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No connection path found")
    
    return {
        "from": {"id": path.start_entity.id, "name": path.start_entity.name},
        "to": {"id": path.end_entity.id, "name": path.end_entity.name},
        "path": [{"id": e.id, "name": e.name, "type": e.entity_type} for e in path.path],
        "distance": path.total_distance,
        "connections": path.relationship_chain
    }


@router.get("/clusters")
async def get_note_clusters(min_shared_entities: int = 2, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    """Get clusters of related notes based on shared entities"""
    clusters = get_related_notes_clusters(db, current_user.id, min_shared_entities)
    return {"clusters": clusters, "count": len(clusters)}


@router.get("/search")
async def search_relationships(query: str, entity_type: str = None, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    """Search for entities across all types or specific type"""
    from sqlalchemy import or_
    import database.models as models
    
    q = db.query(models.Entity).filter(
        models.Entity.owner_id == current_user.id,
        models.Entity.name.ilike(f"%{query}%")
    )
    
    if entity_type:
        q = q.filter(models.Entity.entity_type == entity_type)
    
    entities = q.all()
    return {"query": query, "results": entities}
