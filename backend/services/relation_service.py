"""
Relation Graph Service
Implements graph-based algorithms to discover and analyze relationships between entities.
Uses forest/tree structures to find paths and connections.
"""

from typing import List, Dict, Set, Tuple, Optional
from sqlalchemy.orm import Session
from collections import defaultdict, deque
from database import models
from database.facts import Facts, FactEvidence, RelationType
from datetime import datetime
import re


class EntityNode:
    """Represents a node in the relation graph"""
    def __init__(self, entity_type: str, entity_id: int, name: str):
        self.entity_type = entity_type  # 'person', 'place', 'event'
        self.entity_id = entity_id
        self.name = name
        self.edges: List['RelationEdge'] = []
    
    def __hash__(self):
        return hash((self.entity_type, self.entity_id))
    
    def __eq__(self, other):
        return self.entity_type == other.entity_type and self.entity_id == other.entity_id
    
    def __repr__(self):
        return f"{self.entity_type}({self.entity_id}:{self.name})"


class RelationEdge:
    """Represents an edge (relationship) in the graph"""
    def __init__(self, source: EntityNode, target: EntityNode, relation_type: str, 
                 confidence: int, description: str = ""):
        self.source = source
        self.target = target
        self.relation_type = relation_type
        self.confidence = confidence  # Higher = stronger relation
        self.description = description
    
    def __repr__(self):
        return f"{self.source.name} --[{self.relation_type}({self.confidence})]--> {self.target.name}"


class RelationPath:
    """Represents a path between two entities"""
    def __init__(self, start: EntityNode, end: EntityNode, path: List[RelationEdge]):
        self.start = start
        self.end = end
        self.path = path  # List of edges connecting start to end
        self.length = len(path)
        self.total_confidence = sum(edge.confidence for edge in path) if path else 0
    
    def __repr__(self):
        if not self.path:
            return f"No connection between {self.start.name} and {self.end.name}"
        
        path_str = " -> ".join([self.path[0].source.name] + [edge.target.name for edge in self.path])
        relations = " -> ".join([edge.relation_type for edge in self.path])
        return f"Path ({self.length} hops, confidence={self.total_confidence}): {path_str}\nRelations: {relations}"


class RelationGraph:
    """
    Builds and manages a graph of entity relationships
    Implements BFS for pathfinding and connected component analysis
    """
    
    def __init__(self, db: Session, user_id: int):
        self.db = db
        self.user_id = user_id
        self.nodes: Dict[Tuple[str, int], EntityNode] = {}
        self.edges: List[RelationEdge] = []
        self._build_graph()
    
    def _build_graph(self):
        """Build the entire relation graph from facts in database"""
        # Fetch all facts for this user
        facts = self.db.query(Facts).filter(Facts.user_id == self.user_id).all()
        
        for fact in facts:
            # Get or create nodes
            source_node = self._get_or_create_node(fact.source_type, fact.source_id)
            target_node = self._get_or_create_node(fact.target_type, fact.target_id)
            
            if source_node and target_node:
                # Create edge
                edge = RelationEdge(
                    source=source_node,
                    target=target_node,
                    relation_type=fact.relation_type,
                    confidence=fact.confidence_score,
                    description=fact.description or ""
                )
                self.edges.append(edge)
                source_node.edges.append(edge)
    
    def _get_or_create_node(self, entity_type: str, entity_id: int) -> Optional[EntityNode]:
        """Get or create a node for an entity"""
        key = (entity_type, entity_id)
        
        if key in self.nodes:
            return self.nodes[key]
        
        # Fetch entity from database
        name = None
        if entity_type == 'person':
            person = self.db.query(models.Persons).filter(
                models.Persons.id == entity_id,
                models.Persons.user_id == self.user_id
            ).first()
            if person:
                name = f"{person.first_name} {person.last_name or ''}".strip()
        elif entity_type == 'place':
            place = self.db.query(models.Places).filter(
                models.Places.id == entity_id,
                models.Places.user_id == self.user_id
            ).first()
            if place:
                name = place.name
        elif entity_type == 'event':
            event = self.db.query(models.Events).filter(
                models.Events.id == entity_id,
                models.Events.user_id == self.user_id
            ).first()
            if event:
                name = event.title
        
        if name:
            node = EntityNode(entity_type, entity_id, name)
            self.nodes[key] = node
            return node
        
        return None
    
    def find_path(self, source_type: str, source_id: int, 
                  target_type: str, target_id: int, 
                  max_depth: int = 4) -> Optional[RelationPath]:
        """
        Find shortest path between two entities using BFS
        max_depth limits the search to prevent infinite loops
        """
        source_key = (source_type, source_id)
        target_key = (target_type, target_id)
        
        if source_key not in self.nodes or target_key not in self.nodes:
            return None
        
        source_node = self.nodes[source_key]
        target_node = self.nodes[target_key]
        
        if source_node == target_node:
            return RelationPath(source_node, target_node, [])
        
        # BFS to find shortest path
        queue = deque([(source_node, [])])  # (current_node, path_to_reach_it)
        visited = {source_node}
        
        while queue:
            current_node, path = queue.popleft()
            
            # Check depth limit
            if len(path) >= max_depth:
                continue
            
            # Explore neighbors
            for edge in current_node.edges:
                next_node = edge.target
                
                if next_node == target_node:
                    # Found target!
                    return RelationPath(source_node, target_node, path + [edge])
                
                if next_node not in visited:
                    visited.add(next_node)
                    queue.append((next_node, path + [edge]))
        
        return None
    
    def find_all_paths(self, source_type: str, source_id: int,
                      target_type: str, target_id: int,
                      max_depth: int = 4, max_paths: int = 5) -> List[RelationPath]:
        """Find multiple paths between two entities (up to max_paths)"""
        source_key = (source_type, source_id)
        target_key = (target_type, target_id)
        
        if source_key not in self.nodes or target_key not in self.nodes:
            return []
        
        source_node = self.nodes[source_key]
        target_node = self.nodes[target_key]
        
        paths = []
        
        # DFS to find multiple paths
        def dfs(current, target, path, visited, depth):
            if depth > max_depth or len(paths) >= max_paths:
                return
            
            if current == target:
                paths.append(RelationPath(source_node, target_node, path.copy()))
                return
            
            for edge in current.edges:
                next_node = edge.target
                if next_node not in visited:
                    visited.add(next_node)
                    path.append(edge)
                    dfs(next_node, target, path, visited, depth + 1)
                    path.pop()
                    visited.remove(next_node)
        
        dfs(source_node, target_node, [], {source_node}, 0)
        return sorted(paths, key=lambda p: (-p.total_confidence, p.length))
    
    def find_common_connections(self, entity1_type: str, entity1_id: int,
                               entity2_type: str, entity2_id: int,
                               depth: int = 2) -> Dict[str, List]:
        """
        Find common entities connected to both entities
        Returns entities that both source entities connect to
        """
        key1 = (entity1_type, entity1_id)
        key2 = (entity2_type, entity2_id)
        
        if key1 not in self.nodes or key2 not in self.nodes:
            return {}
        
        # Get neighbors of entity1
        neighbors1 = self._get_neighbors_at_depth(self.nodes[key1], depth)
        # Get neighbors of entity2
        neighbors2 = self._get_neighbors_at_depth(self.nodes[key2], depth)
        
        # Find common neighbors
        common = {}
        for node_key, (path1, depth1) in neighbors1.items():
            if node_key in neighbors2:
                path2, depth2 = neighbors2[node_key]
                node = self.nodes[node_key]
                common[node_key] = {
                    'node': node,
                    'path_from_1': path1,
                    'depth_from_1': depth1,
                    'path_from_2': path2,
                    'depth_from_2': depth2,
                }
        
        return common
    
    def _get_neighbors_at_depth(self, node: EntityNode, depth: int) -> Dict[Tuple[str, int], Tuple[List, int]]:
        """Get all reachable nodes at specific depth from a node"""
        neighbors = {}
        queue = deque([(node, [], 0)])  # (current_node, path_to_reach, current_depth)
        visited = {node}
        
        while queue:
            current, path, current_depth = queue.popleft()
            
            if current != node:  # Don't include the starting node
                key = (current.entity_type, current.entity_id)
                neighbors[key] = (path, current_depth)
            
            if current_depth >= depth:
                continue
            
            for edge in current.edges:
                next_node = edge.target
                if next_node not in visited:
                    visited.add(next_node)
                    queue.append((next_node, path + [edge], current_depth + 1))
        
        return neighbors
    
    def get_entity_neighbors(self, entity_type: str, entity_id: int) -> List[Tuple[EntityNode, str, int]]:
        """Get immediate neighbors of an entity with relation types"""
        key = (entity_type, entity_id)
        if key not in self.nodes:
            return []
        
        node = self.nodes[key]
        return [(edge.target, edge.relation_type, edge.confidence) for edge in node.edges]
    
    def get_connected_components(self) -> List[Set[EntityNode]]:
        """Find all connected components in the graph using Union-Find"""
        if not self.nodes:
            return []
        
        parent = {}
        
        def find(x):
            if x not in parent:
                parent[x] = x
            if parent[x] != x:
                parent[x] = find(parent[x])
            return parent[x]
        
        def union(x, y):
            px, py = find(x), find(y)
            if px != py:
                parent[px] = py
        
        # Union all connected nodes
        for edge in self.edges:
            union(edge.source, edge.target)
        
        # Group by component
        components = defaultdict(set)
        for node in self.nodes.values():
            root = find(node)
            components[root].add(node)
        
        return list(components.values())


def extract_facts_from_note(db: Session, note: models.Notes, user_id: int):
    """
    Extract facts from a note by analyzing entity mentions
    Creates facts for any entities mentioned together in a note
    """
    # Get mentioned entities
    persons = note.mentioned_persons
    places = note.mentioned_places
    events = note.mentioned_events
    
    # Create facts for co-mentions
    # Person-Place co-mentions - use refine_relation_type to determine specific type
    for person in persons:
        for place in places:
            # Analyze note content to determine specific relation type
            relation_type = refine_relation_type(db, note.content or "", person, place)
            _create_or_update_fact(
                db, user_id,
                'person', person.id,
                'place', place.id,
                relation_type,
                description=f"Both mentioned in note: {note.title}"
            )
    
    # Person-Event co-mentions
    for person in persons:
        for event in events:
            _create_or_update_fact(
                db, user_id,
                'person', person.id,
                'event', event.id,
                'attends',  # Default for person-event co-mention
                description=f"Both mentioned in note: {note.title}"
            )
    
    # Person-Person co-mentions
    for i, person1 in enumerate(persons):
        for person2 in persons[i+1:]:
            _create_or_update_fact(
                db, user_id,
                'person', person1.id,
                'person', person2.id,
                'knows',  # Generic person-person relation
                description=f"Both mentioned in note: {note.title}"
            )
    
    # Place-Event co-mentions (event at place)
    for place in places:
        for event in events:
            _create_or_update_fact(
                db, user_id,
                'event', event.id,
                'place', place.id,
                'located_at',
                description=f"Both mentioned in note: {note.title}"
            )


def _create_or_update_fact(db: Session, user_id: int, 
                          source_type: str, source_id: int,
                          target_type: str, target_id: int,
                          relation_type: str,
                          description: str = ""):
    """Create or update a fact in the database"""
    # Check if fact already exists
    fact = db.query(Facts).filter(
        Facts.user_id == user_id,
        Facts.source_type == source_type,
        Facts.source_id == source_id,
        Facts.target_type == target_type,
        Facts.target_id == target_id,
        Facts.relation_type == relation_type
    ).first()
    
    if fact:
        # Increase confidence
        fact.confidence_score += 1
        fact.updated_at = datetime.utcnow()
    else:
        # Create new fact
        fact = Facts(
            user_id=user_id,
            source_type=source_type,
            source_id=source_id,
            target_type=target_type,
            target_id=target_id,
            relation_type=relation_type,
            confidence_score=1,
            description=description
        )
        db.add(fact)
    
    db.flush()
    return fact


def refine_relation_type(db: Session, note_content: str, 
                        person: models.Persons, place: models.Places) -> str:
    """
    Analyze note content to determine specific relation type between person and place
    Uses pattern matching and keywords
    """
    content_lower = note_content.lower()
    
    # Keywords for different relations
    studies_keywords = ['study', 'student', 'studies at', 'education', 'school', 'university', 'college', 'learn']
    works_keywords = ['work', 'works at', 'employee', 'staff', 'job', 'employed', 'position']
    lives_keywords = ['live', 'lives at', 'home', 'address', 'resident', 'resides', 'lives in']
    owns_keywords = ['own', 'owner', 'owns', 'property']
    manages_keywords = ['manage', 'manages', 'manager', 'managing']
    visits_keywords = ['visit', 'visits', 'visited']
    
    # Check for keyword matches
    if any(keyword in content_lower for keyword in studies_keywords):
        return RelationType.STUDIES_AT.value
    if any(keyword in content_lower for keyword in works_keywords):
        return RelationType.WORKS_AT.value
    if any(keyword in content_lower for keyword in lives_keywords):
        return RelationType.LIVES_AT.value
    if any(keyword in content_lower for keyword in owns_keywords):
        return RelationType.OWNS.value
    if any(keyword in content_lower for keyword in manages_keywords):
        return RelationType.MANAGES.value
    if any(keyword in content_lower for keyword in visits_keywords):
        return RelationType.VISITS.value
    
    # Default
    return RelationType.RELATED.value
