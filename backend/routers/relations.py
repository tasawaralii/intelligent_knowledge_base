"""
Relations Router - API endpoints for entity relationship discovery and analysis
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from database.core import get_db
from database import models
from database.facts import Facts
from services.relation_service import RelationGraph, extract_facts_from_note
from services.fact_parser import get_fact_details
from schemas_relations import (
    RelationPath, PathHop, CommonConnection, CommonConnections, EntityNeighbor, EntityNeighbors,
    RelationshipAnalysis, ConnectedComponent, GraphStatistics, ExtractedFact, NoteFacts,
    FactResponse, FactCreate, Facts as FactsSchema
)
from dependencies import get_current_user
from typing import List

router = APIRouter(
    prefix="/api/relations",
    tags=["relations"]
)


def _convert_path_to_response(path, graph) -> RelationPath:
    """Convert RelationPath from service to response schema"""
    hops = []
    for edge in path.path:
        hops.append(PathHop(
            from_entity=edge.source.name,
            to_entity=edge.target.name,
            relation_type=edge.relation_type,
            confidence=edge.confidence
        ))
    
    return RelationPath(
        start_entity_type=path.start.entity_type,
        start_entity_id=path.start.entity_id,
        start_entity_name=path.start.name,
        end_entity_type=path.end.entity_type,
        end_entity_id=path.end.entity_id,
        end_entity_name=path.end.name,
        path_length=path.length,
        total_confidence=path.total_confidence,
        hops=hops
    )


def _get_entity_name(db: Session, entity_type: str, entity_id: int) -> str:
    """Get the name of an entity"""
    if entity_type == 'person':
        person = db.query(models.Persons).filter(models.Persons.id == entity_id).first()
        if person:
            return f"{person.first_name} {person.last_name or ''}".strip()
    elif entity_type == 'place':
        place = db.query(models.Places).filter(models.Places.id == entity_id).first()
        if place:
            return place.name
    elif entity_type == 'event':
        event = db.query(models.Events).filter(models.Events.id == entity_id).first()
        if event:
            return event.title
    return "Unknown"


@router.get("/find-relation/{entity1_type}/{entity1_id}/{entity2_type}/{entity2_id}")
async def find_relation(
    entity1_type: str,
    entity1_id: int,
    entity2_type: str,
    entity2_id: int,
    current_user: models.Users = Depends(get_current_user),
    db: Session = Depends(get_db),
    max_depth: int = Query(4, ge=1, le=10)
):
    """
    Find relationships between two entities
    
    Returns:
    - Whether entities are directly connected
    - Shortest path between them
    - All possible paths
    - Common connections
    - Confidence levels
    """
    try:
        graph = RelationGraph(db, current_user.id)
        
        # Get entity names
        entity1_name = _get_entity_name(db, entity1_type, entity1_id)
        entity2_name = _get_entity_name(db, entity2_type, entity2_id)
        
        # Find shortest path
        shortest_path = graph.find_path(entity1_type, entity1_id, entity2_type, entity2_id, max_depth)
        
        # Find all paths
        all_paths = graph.find_all_paths(entity1_type, entity1_id, entity2_type, entity2_id, max_depth)
        
        # Find common connections
        common_connections_dict = graph.find_common_connections(
            entity1_type, entity1_id,
            entity2_type, entity2_id,
            depth=2
        )
        
        # Convert common connections
        common_connections = []
        for node_key, conn_data in common_connections_dict.items():
            node = conn_data['node']
            path1_hops = [PathHop(
                from_entity=edge.source.name,
                to_entity=edge.target.name,
                relation_type=edge.relation_type,
                confidence=edge.confidence
            ) for edge in conn_data['path_from_1']]
            
            path2_hops = [PathHop(
                from_entity=edge.source.name,
                to_entity=edge.target.name,
                relation_type=edge.relation_type,
                confidence=edge.confidence
            ) for edge in conn_data['path_from_2']]
            
            common_connections.append(CommonConnection(
                entity_type=node.entity_type,
                entity_id=node.entity_id,
                entity_name=node.name,
                path_from_first=path1_hops,
                depth_from_first=conn_data['depth_from_1'],
                path_from_second=path2_hops,
                depth_from_second=conn_data['depth_from_2'],
            ))
        
        # Determine if directly connected
        is_directly_connected = shortest_path is not None and shortest_path.length == 1
        
        # Calculate confidence level
        if not shortest_path:
            confidence_level = "none"
            connection_strength = 0
        elif shortest_path.length <= 1:
            confidence_level = "high"
            connection_strength = min(100, shortest_path.total_confidence * 20)
        elif shortest_path.length == 2:
            confidence_level = "medium"
            connection_strength = min(100, shortest_path.total_confidence * 15)
        else:
            confidence_level = "low"
            connection_strength = min(100, shortest_path.total_confidence * 10)
        
        # Build summary
        if is_directly_connected:
            relation_summary = f"{entity1_name} and {entity2_name} are directly related through {shortest_path.path[0].relation_type}"
        elif shortest_path:
            relations = " → ".join([edge.relation_type for edge in shortest_path.path])
            relation_summary = f"Connection found: {entity1_name} and {entity2_name} are connected through {shortest_path.length} intermediaries. Relations: {relations}"
        else:
            relation_summary = f"No connection found between {entity1_name} and {entity2_name} within {max_depth} hops"
        
        return RelationshipAnalysis(
            entities=[
                {"type": entity1_type, "id": entity1_id, "name": entity1_name},
                {"type": entity2_type, "id": entity2_id, "name": entity2_name}
            ],
            are_directly_connected=is_directly_connected,
            shortest_path=_convert_path_to_response(shortest_path, graph) if shortest_path else None,
            all_paths=[_convert_path_to_response(path, graph) for path in all_paths[:5]],
            common_connections=common_connections[:10],
            relation_summary=relation_summary,
            confidence_level=confidence_level,
            connection_strength=connection_strength
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/neighbors/{entity_type}/{entity_id}")
async def get_entity_neighbors(
    entity_type: str,
    entity_id: int,
    current_user: models.Users = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all immediate neighbors (directly connected entities) of an entity
    """
    try:
        graph = RelationGraph(db, current_user.id)
        entity_name = _get_entity_name(db, entity_type, entity_id)
        
        neighbors_data = graph.get_entity_neighbors(entity_type, entity_id)
        
        neighbors = [
            EntityNeighbor(
                entity_type=target_node.entity_type,
                entity_id=target_node.entity_id,
                entity_name=target_node.name,
                relation_type=relation_type,
                confidence=confidence
            )
            for target_node, relation_type, confidence in neighbors_data
        ]
        
        return EntityNeighbors(
            entity_type=entity_type,
            entity_id=entity_id,
            entity_name=entity_name,
            neighbors=neighbors,
            total_neighbors=len(neighbors)
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/graph-stats")
async def get_graph_statistics(
    current_user: models.Users = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get statistics about the entity relation graph
    """
    try:
        graph = RelationGraph(db, current_user.id)
        
        components = graph.get_connected_components()
        total_relations = len(graph.edges)
        
        if components:
            largest_component = max(len(comp) for comp in components)
        else:
            largest_component = 0
        
        # Calculate density (actual edges / possible edges)
        total_entities = len(graph.nodes)
        if total_entities > 1:
            max_possible_edges = total_entities * (total_entities - 1) / 2
            density = total_relations / max_possible_edges if max_possible_edges > 0 else 0
        else:
            density = 0
        
        return GraphStatistics(
            total_entities=total_entities,
            total_relations=total_relations,
            total_connected_components=len(components),
            largest_component_size=largest_component,
            average_path_length=0,  # Could be calculated for specific components
            graph_density=density
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/connected-components")
async def get_connected_components(
    current_user: models.Users = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all connected components in the graph
    Useful for finding groups of related entities
    """
    try:
        graph = RelationGraph(db, current_user.id)
        components = graph.get_connected_components()
        
        result = []
        for i, component in enumerate(sorted(components, key=len, reverse=True)):
            entities = []
            for node in component:
                entities.append({
                    "type": node.entity_type,
                    "id": node.entity_id,
                    "name": node.name
                })
            
            result.append(ConnectedComponent(
                component_id=i,
                entity_count=len(component),
                entities=entities
            ))
        
        return {"components": result, "total_components": len(result)}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/extract-facts/{note_id}")
async def extract_note_facts(
    note_id: int,
    current_user: models.Users = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Extract and analyze facts from a specific note
    """
    try:
        note = db.query(models.Notes).filter(
            models.Notes.id == note_id,
            models.Notes.owner_id == current_user.id
        ).first()
        
        if not note:
            raise HTTPException(status_code=404, detail="Note not found")
        
        # Extract facts from note
        extract_facts_from_note(db, note, current_user.id)
        
        # Get all facts extracted from this note
        facts = db.query(Facts).filter(
            Facts.user_id == current_user.id
        ).all()
        
        extracted_facts = []
        for fact in facts:
            source_name = _get_entity_name(db, fact.source_type, fact.source_id)
            target_name = _get_entity_name(db, fact.target_type, fact.target_id)
            
            extracted_facts.append(ExtractedFact(
                source_type=fact.source_type,
                source_id=fact.source_id,
                source_name=source_name,
                target_type=fact.target_type,
                target_id=fact.target_id,
                target_name=target_name,
                relation_type=fact.relation_type,
                confidence=fact.confidence_score,
                evidence_notes=1
            ))
        
        db.commit()
        
        return NoteFacts(
            note_id=note.id,
            note_title=note.title or "",
            facts_extracted=extracted_facts,
            total_facts=len(extracted_facts)
        )
    
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/facts")
async def get_all_facts(
    current_user: models.Users = Depends(get_current_user),
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000)
):
    """
    Get all facts for current user
    """
    try:
        facts = db.query(Facts).filter(
            Facts.user_id == current_user.id
        ).order_by(Facts.confidence_score.desc()).offset(skip).limit(limit).all()
        
        facts_data = [FactResponse.model_validate(fact) for fact in facts]
        
        return FactsSchema(facts=facts_data)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/facts", response_model=FactResponse)
async def create_fact(
    fact: FactCreate,
    current_user: models.Users = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Manually create a fact between two entities
    """
    try:
        db_fact = Facts(
            user_id=current_user.id,
            source_type=fact.source_type,
            source_id=fact.source_id,
            target_type=fact.target_type,
            target_id=fact.target_id,
            relation_type=fact.relation_type,
            confidence_score=fact.confidence_score,
            description=fact.description
        )
        db.add(db_fact)
        db.commit()
        db.refresh(db_fact)
        
        return FactResponse.model_validate(db_fact)
    
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/common-ground/{entity1_type}/{entity1_id}/{entity2_type}/{entity2_id}")
async def find_common_ground(
    entity1_type: str,
    entity1_id: int,
    entity2_type: str,
    entity2_id: int,
    current_user: models.Users = Depends(get_current_user),
    db: Session = Depends(get_db),
    depth: int = Query(2, ge=1, le=5)
):
    """
    Find what two entities have in common (shared connections, interests, etc)
    Example: Person A and Person B both study at University X, work with Person C
    """
    try:
        graph = RelationGraph(db, current_user.id)
        
        entity1_name = _get_entity_name(db, entity1_type, entity1_id)
        entity2_name = _get_entity_name(db, entity2_type, entity2_id)
        
        common_dict = graph.find_common_connections(
            entity1_type, entity1_id,
            entity2_type, entity2_id,
            depth=depth
        )
        
        connections = []
        for node_key, conn_data in common_dict.items():
            node = conn_data['node']
            
            # Convert paths to hops
            path1_hops = []
            for edge in conn_data['path_from_1']:
                path1_hops.append(PathHop(
                    from_entity=edge.source.name,
                    to_entity=edge.target.name,
                    relation_type=edge.relation_type,
                    confidence=edge.confidence
                ))
            
            path2_hops = []
            for edge in conn_data['path_from_2']:
                path2_hops.append(PathHop(
                    from_entity=edge.source.name,
                    to_entity=edge.target.name,
                    relation_type=edge.relation_type,
                    confidence=edge.confidence
                ))
            
            connections.append(CommonConnection(
                entity_type=node.entity_type,
                entity_id=node.entity_id,
                entity_name=node.name,
                path_from_first=path1_hops,
                depth_from_first=conn_data['depth_from_1'],
                path_from_second=path2_hops,
                depth_from_second=conn_data['depth_from_2']
            ))
        
        return CommonConnections(
            first_entity_type=entity1_type,
            first_entity_id=entity1_id,
            first_entity_name=entity1_name,
            second_entity_type=entity2_type,
            second_entity_id=entity2_id,
            second_entity_name=entity2_name,
            connections=connections,
            total_connections=len(connections)
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/facts/{fact_id}")
def get_fact(
    fact_id: int,
    db: Session = Depends(get_db),
    current_user: models.Users = Depends(get_current_user)
):
    """
    Get detailed information about a specific fact by ID
    Used for rendering @f.{id} references in notes
    
    Returns:
        Fact details including source/target entities, relation type, confidence
    
    Example response:
    ```json
    {
        "id": 1,
        "source": {"type": "person", "id": 5, "name": "John Doe"},
        "target": {"type": "place", "id": 3, "name": "UET"},
        "relation_type": "studies_at",
        "confidence": 10,
        "description": "@p.john studies at @pl.uet",
        "created_at": "2025-12-28T10:30:00"
    }
    ```
    """
    fact_details = get_fact_details(fact_id, current_user.id, db)
    
    if not fact_details:
        raise HTTPException(status_code=404, detail="Fact not found")
    
    return fact_details

