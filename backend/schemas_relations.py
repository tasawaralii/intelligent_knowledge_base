"""
Relation Schemas - Pydantic models for relation detection API
"""

from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import List, Optional


class FactBase(BaseModel):
    source_type: str  # 'person', 'place', 'event'
    source_id: int
    target_type: str
    target_id: int
    relation_type: str
    confidence_score: int = 1
    description: Optional[str] = None


class FactCreate(FactBase):
    pass


class FactResponse(FactBase):
    id: int
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)


class Facts(BaseModel):
    facts: List[FactResponse]
    model_config = ConfigDict(from_attributes=True)


# Edge representation for paths
class RelationEdgeResponse(BaseModel):
    source_type: str
    source_id: int
    source_name: str
    target_type: str
    target_id: int
    target_name: str
    relation_type: str
    confidence: int


class PathHop(BaseModel):
    from_entity: str  # "Person Name" or "Place Name" etc
    to_entity: str
    relation_type: str
    confidence: int


class RelationPath(BaseModel):
    """Represents a path between two entities"""
    start_entity_type: str
    start_entity_id: int
    start_entity_name: str
    
    end_entity_type: str
    end_entity_id: int
    end_entity_name: str
    
    path_length: int  # Number of hops
    total_confidence: int  # Sum of confidence scores
    hops: List[PathHop]
    
    def __repr__(self):
        path_str = f"{self.start_entity_name}"
        for hop in self.hops:
            path_str += f" --[{hop.relation_type}]--> {hop.to_entity}"
        return path_str


class CommonConnection(BaseModel):
    """A common entity that connects two entities"""
    entity_type: str
    entity_id: int
    entity_name: str
    
    path_from_first: List[PathHop]
    depth_from_first: int
    
    path_from_second: List[PathHop]
    depth_from_second: int


class CommonConnections(BaseModel):
    """Common connections between two entities"""
    first_entity_type: str
    first_entity_id: int
    first_entity_name: str
    
    second_entity_type: str
    second_entity_id: int
    second_entity_name: str
    
    connections: List[CommonConnection]
    total_connections: int


class EntityNeighbor(BaseModel):
    """An immediate neighbor of an entity"""
    entity_type: str
    entity_id: int
    entity_name: str
    relation_type: str
    confidence: int


class EntityNeighbors(BaseModel):
    """All immediate neighbors of an entity"""
    entity_type: str
    entity_id: int
    entity_name: str
    neighbors: List[EntityNeighbor]
    total_neighbors: int


class RelationshipAnalysis(BaseModel):
    """Complete analysis of relationship between two entities"""
    entities: List[dict]  # Basic info about both entities
    are_directly_connected: bool
    shortest_path: Optional[RelationPath]
    all_paths: List[RelationPath]
    common_connections: List[CommonConnection]
    relation_summary: str
    confidence_level: str  # high, medium, low
    connection_strength: int  # 0-100


# Graph Analysis
class ConnectedComponent(BaseModel):
    """A connected component in the relation graph"""
    component_id: int
    entity_count: int
    entities: List[dict]  # List of {type, id, name}


class GraphStatistics(BaseModel):
    """Statistics about the relation graph"""
    total_entities: int
    total_relations: int
    total_connected_components: int
    largest_component_size: int
    average_path_length: float
    graph_density: float


# Relation extraction
class ExtractedFact(BaseModel):
    """A fact extracted from a note"""
    source_type: str
    source_id: int
    source_name: str
    target_type: str
    target_id: int
    target_name: str
    relation_type: str
    confidence: int
    evidence_notes: int  # How many notes support this


class NoteFacts(BaseModel):
    """All facts extracted from a note"""
    note_id: int
    note_title: str
    facts_extracted: List[ExtractedFact]
    total_facts: int
