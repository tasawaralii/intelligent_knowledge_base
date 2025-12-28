# Relation Detection System - Implementation Guide

## Overview
The relation detection system analyzes facts stored in notes and builds a knowledge graph to discover indirect relationships between entities (Person, Place, Event).

### Key Features
1. **Automatic Fact Extraction** - Extracts relationships from notes when entities are co-mentioned
2. **Relation Graph** - Builds a graph structure from extracted facts
3. **Path Finding** - Finds connections between any two entities using BFS
4. **Common Ground Analysis** - Finds shared connections between entities
5. **Graph Statistics** - Provides insights about the entity network

---

## Architecture

### Database Schema

#### Facts Table
Stores discovered relationships between entities:
```
Facts:
- id (primary key)
- user_id (foreign key to users)
- source_type: 'person', 'place', 'event'
- source_id: ID of source entity
- target_type: 'person', 'place', 'event'
- target_id: ID of target entity
- relation_type: Type of relationship (studies_at, works_at, etc.)
- confidence_score: How many times this fact appears
- description: Natural language description
- created_at, updated_at: Timestamps
```

#### FactEvidence Table
Links facts to supporting notes:
```
FactEvidence:
- id (primary key)
- fact_id (foreign key to facts)
- note_id (foreign key to notes)
- context_text: Relevant excerpt from note
- created_at: When evidence was recorded
```

### Services

#### RelationGraph Class
Core data structure for analyzing relationships:

**Main Methods:**
- `find_path()` - Find shortest path between two entities (BFS)
- `find_all_paths()` - Find multiple paths between entities (DFS, up to 5 paths)
- `find_common_connections()` - Find shared connections between entities
- `get_entity_neighbors()` - Get immediate connections of an entity
- `get_connected_components()` - Find all relationship clusters

**Algorithm Details:**

**BFS Path Finding:**
```
1. Start from source entity
2. Explore level-by-level (breadth-first)
3. Track visited nodes to avoid cycles
4. Return first path to target
5. Respects max_depth to prevent infinite searches
```

**DFS Multiple Paths:**
```
1. Start from source entity
2. Explore depth-first with backtracking
3. Track all paths that reach target
4. Return up to 5 best paths (sorted by confidence)
5. Limits depth to prevent explosion
```

**Connected Components (Union-Find):**
```
1. Create parent mapping for all nodes
2. Union nodes connected by edges
3. Group nodes by root parent
4. Return list of independent clusters
```

---

## API Endpoints

### 1. Find Relation Between Two Entities
```
GET /api/relations/find-relation/{entity1_type}/{entity1_id}/{entity2_type}/{entity2_id}
```

**Parameters:**
- `entity1_type`: 'person', 'place', 'event'
- `entity1_id`: ID of first entity
- `entity2_type`: 'person', 'place', 'event'
- `entity2_id`: ID of second entity
- `max_depth`: Max hops to search (1-10, default 4)

**Response:**
```json
{
  "entities": [
    {"type": "person", "id": 1, "name": "John Doe"},
    {"type": "person", "id": 2, "name": "Jane Smith"}
  ],
  "are_directly_connected": false,
  "shortest_path": {
    "start_entity_type": "person",
    "start_entity_id": 1,
    "start_entity_name": "John Doe",
    "end_entity_type": "person",
    "end_entity_id": 2,
    "end_entity_name": "Jane Smith",
    "path_length": 2,
    "total_confidence": 2,
    "hops": [
      {
        "from_entity": "John Doe",
        "to_entity": "UET University",
        "relation_type": "studies_at",
        "confidence": 1
      },
      {
        "from_entity": "UET University",
        "to_entity": "Jane Smith",
        "relation_type": "studies_at",
        "confidence": 1
      }
    ]
  },
  "all_paths": [...],
  "common_connections": [...],
  "relation_summary": "Connection found: John Doe and Jane Smith are connected through 1 intermediaries. Relations: studies_at → studies_at",
  "confidence_level": "medium",
  "connection_strength": 45
}
```

### 2. Get Entity Neighbors
```
GET /api/relations/neighbors/{entity_type}/{entity_id}
```

**Response:**
```json
{
  "entity_type": "person",
  "entity_id": 1,
  "entity_name": "John Doe",
  "neighbors": [
    {
      "entity_type": "place",
      "entity_id": 1,
      "entity_name": "UET University",
      "relation_type": "studies_at",
      "confidence": 3
    },
    {
      "entity_type": "person",
      "entity_id": 3,
      "entity_name": "Ahmed Khan",
      "relation_type": "knows",
      "confidence": 2
    }
  ],
  "total_neighbors": 2
}
```

### 3. Find Common Ground
```
GET /api/relations/common-ground/{entity1_type}/{entity1_id}/{entity2_type}/{entity2_id}
```

**Response:** Shows what two entities have in common
```json
{
  "first_entity_type": "person",
  "first_entity_id": 1,
  "first_entity_name": "John Doe",
  "second_entity_type": "person",
  "second_entity_id": 2,
  "second_entity_name": "Jane Smith",
  "connections": [
    {
      "entity_type": "place",
      "entity_id": 1,
      "entity_name": "UET University",
      "path_from_first": [
        {
          "from_entity": "John Doe",
          "to_entity": "UET University",
          "relation_type": "studies_at",
          "confidence": 1
        }
      ],
      "depth_from_first": 1,
      "path_from_second": [
        {
          "from_entity": "Jane Smith",
          "to_entity": "UET University",
          "relation_type": "studies_at",
          "confidence": 1
        }
      ],
      "depth_from_second": 1
    }
  ],
  "total_connections": 1
}
```

### 4. Graph Statistics
```
GET /api/relations/graph-stats
```

**Response:**
```json
{
  "total_entities": 50,
  "total_relations": 150,
  "total_connected_components": 5,
  "largest_component_size": 35,
  "average_path_length": 2.5,
  "graph_density": 0.12
}
```

### 5. Connected Components
```
GET /api/relations/connected-components
```

**Response:** Shows groups of related entities
```json
{
  "components": [
    {
      "component_id": 0,
      "entity_count": 35,
      "entities": [
        {"type": "person", "id": 1, "name": "John Doe"},
        {"type": "place", "id": 1, "name": "UET University"},
        ...
      ]
    }
  ],
  "total_components": 5
}
```

### 6. Extract Facts from Note
```
POST /api/relations/extract-facts/{note_id}
```

**Response:**
```json
{
  "note_id": 1,
  "note_title": "UET Security",
  "facts_extracted": [
    {
      "source_type": "person",
      "source_id": 1,
      "source_name": "John Doe",
      "target_type": "place",
      "target_id": 1,
      "target_name": "UET University",
      "relation_type": "studies_at",
      "confidence": 1,
      "evidence_notes": 1
    }
  ],
  "total_facts": 1
}
```

### 7. Get All Facts
```
GET /api/relations/facts?skip=0&limit=100
```

### 8. Create Fact Manually
```
POST /api/relations/facts
```

**Body:**
```json
{
  "source_type": "person",
  "source_id": 1,
  "target_type": "place",
  "target_id": 1,
  "relation_type": "works_at",
  "confidence_score": 2,
  "description": "John works as security guard at UET"
}
```

---

## Usage Examples

### Example 1: Checking if Two People Are Related
```python
# Find relation between Person A and Person X
# Person A studies at UET
# Person X is security guard at UET

GET /api/relations/find-relation/person/1/person/2?max_depth=4

# Response shows they're connected through UET
# path_length: 1 (through common place)
# confidence: high
# relation_summary: "Connection found through shared place (UET)"
```

### Example 2: Finding Common Ground
```python
# What do Person A and Person B have in common?

GET /api/relations/common-ground/person/1/person/2

# Response shows all shared connections:
# - Both study at UET University
# - Both work at XYZ Company
# - Both attended Event Z
```

### Example 3: Graph Analysis
```python
# Understand the overall network

GET /api/relations/graph-stats
# Shows total entities, connections, clusters

GET /api/relations/connected-components
# Shows which entities form separate groups
```

### Example 4: Person Details with Network
```python
# Get all people related to a specific person

GET /api/relations/neighbors/person/1

# Response shows:
# - Places they're connected to (study, work, live)
# - Events they attended
# - Other people they're related to
# - How strong each relationship is
```

---

## Relation Types

### Person ↔ Place Relations
- `studies_at` - Person studies at place
- `works_at` - Person works at place
- `lives_at` - Person lives at place
- `visits` - Person visits place
- `owns` - Person owns place
- `manages` - Person manages place

### Person ↔ Event Relations
- `attends` - Person attends event
- `organizes` - Person organizes event
- `participates` - Person participates in event
- `hosts` - Person hosts event

### Person ↔ Person Relations
- `knows` - Persons know each other
- `works_with` - Persons work together
- `related_to` - Persons are related
- `friend_of` - Persons are friends
- `colleague_of` - Persons are colleagues
- `supervisor_of` - Person supervises another
- `subordinate_of` - Person works under another

### Place ↔ Event Relations
- `located_at` - Event is at place
- `hosted_at` - Event is hosted at place

### Generic
- `related` - Generic relation when type is unclear

---

## How Facts Are Extracted

When a note is created/updated:

1. **Entity Extraction** - System identifies all mentioned persons, places, and events
2. **Co-mention Analysis** - Any entities mentioned together in same note get linked
3. **Relation Type Inference** - Keywords in note content help determine specific relation type
4. **Confidence Building** - If same relation appears in multiple notes, confidence increases
5. **Graph Update** - RelationGraph is rebuilt to include new facts

**Example:**
```
Note: "John studies at UET. He is a student there."
Entities: Person(John) + Place(UET)
Extracted Fact: John --studies_at--> UET (confidence=1)

Later note: "John is at UET campus"
Extracted Fact: John --studies_at--> UET (confidence=2)
```

---

## Algorithm Complexity

| Operation | Complexity | Notes |
|-----------|-----------|-------|
| Build Graph | O(F + E) | F = facts, E = edges |
| Find Shortest Path (BFS) | O(V + E) | V = entities, E = relations |
| Find All Paths (DFS) | O(V^depth) | Limited to max_depth |
| Common Connections | O(V + E) | For each depth level |
| Connected Components | O(V + E) | Union-find with path compression |

---

## Integration with Existing System

### For Note Creation
Facts are automatically extracted when you POST a note:
```python
# In note_service.py create_note()
extract_facts_from_note(db, db_note, owner_id)
```

### For Note Updates
Facts are re-extracted when note content changes:
```python
# In note_service.py update_note()
extract_facts_from_note(db, db_note, owner_id)
```

### Frontend Integration
1. After showing a note, call `/api/relations/extract-facts/{note_id}` to ensure facts are captured
2. When displaying a person, show their network using `/api/relations/neighbors/person/{id}`
3. In search/discovery features, use `/api/relations/find-relation/...` to suggest connections

---

## Performance Considerations

1. **Graph Caching** - RelationGraph is built fresh each request (can be optimized with caching)
2. **Path Depth Limits** - Default max_depth=4 prevents exponential path explosion
3. **Batching** - Multiple queries can be combined
4. **Indexing** - Facts table should have indexes on:
   - (user_id, source_type, source_id)
   - (user_id, target_type, target_id)
   - (user_id, relation_type)

---

## Future Enhancements

1. **Machine Learning** - Learn relation types from context automatically
2. **Temporal Relations** - Track when relations were active
3. **Relation Weights** - Probabilistic confidence instead of just counts
4. **Query Language** - Complex queries like "Find all persons who work at places in Lahore"
5. **Visualization** - Generate graph visualizations
6. **Recommendations** - Suggest possible connections to explore
7. **Cache Layer** - Redis caching of frequently accessed graphs
8. **Incremental Updates** - Update graph incrementally instead of rebuilding

