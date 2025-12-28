"""
Test Cases and Examples for Relation Detection System
Demonstrates how the system discovers relations between entities
"""

# ============================================================================
# EXAMPLE 1: Basic Person-Place Relation Detection
# ============================================================================

"""
Scenario: John studies at UET

Steps:
1. Create Person: John
2. Create Place: UET University
3. Create Note mentioning both:
   - Title: "John's Education"
   - Content: "@p.john studies at @pl.uet since 2020"

Result:
- Fact created: John --studies_at--> UET (confidence=1)
- API call: GET /api/relations/neighbors/person/{john_id}
  Returns: John is connected to UET through 'studies_at' relation
"""

# ============================================================================
# EXAMPLE 2: Indirect Person-Person Relation Through Place
# ============================================================================

"""
Scenario: Finding connection between Person A and Person B

Setup:
- Person A (John) studies at UET
- Person B (Jane) is security guard at UET
- Note 1: "@p.john studies at @pl.uet"
- Note 2: "@p.jane works at @pl.uet"

Process:
1. Extract facts from Note 1: John --studies_at--> UET
2. Extract facts from Note 2: Jane --works_at--> UET
3. System builds graph:
   John --studies_at--> UET <--works_at-- Jane

Query:
- GET /api/relations/find-relation/person/{john_id}/person/{jane_id}

Result:
{
  "are_directly_connected": false,
  "shortest_path": {
    "path_length": 2,
    "hops": [
      "John --studies_at--> UET",
      "UET <--works_at-- Jane"
    ],
    "total_confidence": 2,
    "relation_summary": "John and Jane both connected to UET University"
  },
  "connection_strength": 45,
  "confidence_level": "medium"
}

API Call for Common Ground:
- GET /api/relations/common-ground/person/{john_id}/person/{jane_id}

Result: Shows both are connected to UET, making them indirectly related
"""

# ============================================================================
# EXAMPLE 3: Complex Multi-Hop Path Finding
# ============================================================================

"""
Scenario: Finding distant connections

Entity Map:
- Person A studies at University X
- Person B works with Person A
- Person C attended Event at University X
- Person D attends Event Y with Person C

Query: Is Person A related to Person D?

Path Discovery (BFS):
Hop 1: Person A -> University X (studies_at)
Hop 2: University X -> Event (located_at)
Hop 3: Event -> Person C (attends)
Hop 4: Person C -> Event Y (attends)
Hop 5: Event Y -> Person D (attends)

Result:
- Found path of length 5
- Confidence medium due to length
- Shows chain of connections that link them

Common Ground Analysis:
- Both connected to University X ecosystem
- Both involved with events
"""

# ============================================================================
# EXAMPLE 4: Confidence Building Through Multiple Notes
# ============================================================================

"""
Scenario: Strengthening confidence through repeated mentions

Day 1:
Note: "@p.ahmed works at @pl.uet security"
Fact: Ahmed --works_at--> UET (confidence=1)

Day 2:
Note: "@p.ahmed is security officer at @pl.uet"
Fact: Ahmed --works_at--> UET (confidence=2, updated)

Day 3:
Note: "@p.ahmed manages @pl.uet gates"
Fact: Ahmed --manages--> UET (confidence=1, new relation)
Fact: Ahmed --works_at--> UET (confidence=3, existing increases)

Result:
- System tracks confidence score
- Multiple evidence points strengthen relations
- Graph shows highly confident connections first
- Useful for finding core relationships vs weak connections
"""

# ============================================================================
# EXAMPLE 5: Connected Components Discovery
# ============================================================================

"""
Scenario: Finding communities/groups within your knowledge base

Setup:
Group 1 (University Community):
- John, Ahmed, Fatima (persons)
- UET University, Library (places)
- Seminar, Conference (events)
All heavily interconnected

Group 2 (Work Community):
- Alice, Bob, Charlie (persons)
- Tech Company, Office (places)
- Team Meeting, Project (events)
All interconnected

Isolated:
- Eve (person with no relations)

Query:
- GET /api/relations/connected-components

Result:
{
  "total_components": 3,
  "components": [
    {
      "component_id": 0,
      "entity_count": 7,
      "largest_community": true,
      "entities": [John, Ahmed, Fatima, UET, Library, Seminar, Conference]
    },
    {
      "component_id": 1,
      "entity_count": 5,
      "entities": [Alice, Bob, Charlie, TechCo, Office]
    },
    {
      "component_id": 2,
      "entity_count": 1,
      "entities": [Eve]
    }
  ]
}

Interpretation:
- Shows natural groupings in your knowledge base
- Useful for organizing and understanding entity clusters
- Identifies isolated entities that need connections
"""

# ============================================================================
# EXAMPLE 6: Real-World Use Case - Police Investigation
# ============================================================================

"""
Scenario: Finding connections in criminal investigation

Setup:
Notes about suspects and locations:

Note 1: "Suspect A was seen at Library on Wednesday"
Note 2: "Suspect B works at Library as security guard"
Note 3: "Witness C also works at Library"
Note 4: "Suspect A was at Shopping Center on Thursday"
Note 5: "Suspect B visits Shopping Center often"

Graph Built:
Suspect A --at--> Library <--works_at-- Suspect B
Suspect A --at--> Shopping Center <--visits-- Suspect B

Query: Are Suspect A and B connected?

Result:
- Found 2 paths of length 1 (direct connection through locations)
- Common connections: Library, Shopping Center
- Confidence: HIGH
- System answer: "Yes, both suspects connected through shared locations"

Use: Helps investigators identify persons of interest who may be working together
"""

# ============================================================================
# EXAMPLE 7: Graph Statistics and Network Health
# ============================================================================

"""
Query: GET /api/relations/graph-stats

Result:
{
  "total_entities": 156,
  "total_relations": 423,
  "total_connected_components": 3,
  "largest_component_size": 145,
  "average_path_length": 2.3,
  "graph_density": 0.18
}

Interpretation:
- 156 entities with 423 connections
- Most entities (145) are in same component - well-connected knowledge base
- Average path length 2.3 means most entities reach each other in 2-3 hops
- Graph density 0.18 means ~18% of possible connections exist
  (Not fully connected, which is normal)

Insights:
- If density too high (>0.5): May indicate redundant facts
- If density too low (<0.05): Knowledge base may be fragmented
- Large isolated components suggest separate domains
"""

# ============================================================================
# EXAMPLE 8: Temporal Relations (Future Feature)
# ============================================================================

"""
Scenario: Relations that change over time

Current facts don't include time, but could be enhanced:

Person: John
- 2020-2023: studies_at UET
- 2023-present: works_at TechCorp
- 2020-present: knows Ahmed

Query: Who did John know at UET (in 2022)?

With temporal support:
- Would find Ahmed (studies_at UET in 2022)
- Would exclude contacts made after leaving UET

This would require:
- Adding start_date, end_date to facts
- Temporal queries in graph traversal
- Time-aware path finding
"""

# ============================================================================
# API CALL EXAMPLES
# ============================================================================

# 1. Find relation between two persons
curl -X GET "http://localhost:8000/api/relations/find-relation/person/1/person/2?max_depth=4" \
  -H "Authorization: Bearer {token}"

# 2. Get all neighbors of a person
curl -X GET "http://localhost:8000/api/relations/neighbors/person/1" \
  -H "Authorization: Bearer {token}"

# 3. Find common ground between two entities
curl -X GET "http://localhost:8000/api/relations/common-ground/person/1/person/2?depth=2" \
  -H "Authorization: Bearer {token}"

# 4. Get all connected components
curl -X GET "http://localhost:8000/api/relations/connected-components" \
  -H "Authorization: Bearer {token}"

# 5. Get graph statistics
curl -X GET "http://localhost:8000/api/relations/graph-stats" \
  -H "Authorization: Bearer {token}"

# 6. Extract facts from a note
curl -X POST "http://localhost:8000/api/relations/extract-facts/1" \
  -H "Authorization: Bearer {token}"

# 7. Create a fact manually
curl -X POST "http://localhost:8000/api/relations/facts" \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{
    "source_type": "person",
    "source_id": 1,
    "target_type": "place",
    "target_id": 5,
    "relation_type": "works_at",
    "confidence_score": 2,
    "description": "John is senior engineer at TechCorp"
  }'

# 8. Get all facts
curl -X GET "http://localhost:8000/api/relations/facts?skip=0&limit=50" \
  -H "Authorization: Bearer {token}"

# ============================================================================
# TESTING CHECKLIST
# ============================================================================

Testing Plan:
□ Create persons with different relationships
□ Create places and events
□ Create notes mentioning multiple entities
□ Test fact extraction on note creation
□ Test fact extraction on note update
□ Query neighbors of each entity type
□ Find paths between persons
□ Find paths between person and place
□ Find paths between person and event
□ Test max_depth parameter
□ Find common ground between entities
□ Get graph statistics
□ Get connected components
□ Create facts manually
□ Update facts (re-mention in notes)
□ Test confidence scoring
□ Test with 100+ entities
□ Test performance with deep graphs
□ Test edge cases (isolated entities)
□ Test circular references

Expected Results:
- System finds all valid paths
- Confidence scores increase with multiple mentions
- Graph statistics are accurate
- No false connections created
- Performance acceptable (<100ms for typical queries)
"""
