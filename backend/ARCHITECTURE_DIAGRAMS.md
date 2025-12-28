"""
VISUAL ARCHITECTURE GUIDE - Relation Detection System
"""

═══════════════════════════════════════════════════════════════════════════════
GRAPH STRUCTURE VISUALIZATION
═══════════════════════════════════════════════════════════════════════════════

SIMPLE EXAMPLE: 2 People Connected Through a Place

    Person: John              Person: Jane
        ●                         ●
        │                         │
        │ studies_at              │ works_at
        │ (confidence: 2)         │ (confidence: 3)
        └──────────→ ● ←──────────┘
                   Place: UET
    
Query: find-relation(John, Jane)
Response:
├─ Are directly connected: NO
├─ Shortest path:
│  └─ John --studies_at--> UET --works_at--> Jane
│     (2 hops, confidence: 5)
├─ Common connections:
│  └─ UET University
└─ Confidence level: MEDIUM


═══════════════════════════════════════════════════════════════════════════════
COMPLEX EXAMPLE: Multi-Hop Relationships

Network Structure:

    Person             Event              Place
    Ahmed ────knows──→ Seminar  ←──hosted_at── UET
      │                  ↑                      ↑
      │                  │                      │
      studies_at      attends              located_at
      │                  │                      │
      └─────────────→ Fatima ────works_at─────┘
    

Facts in System:
├─ Ahmed knows Fatima
├─ Ahmed studies_at UET
├─ Fatima works_at UET
├─ Fatima attends Seminar
├─ Seminar located_at UET

Possible Queries:

Q1: find-relation(Ahmed, Seminar)
A: Ahmed → studies_at → UET → located_at → Seminar (2 hops)

Q2: find-relation(Ahmed, Fatima)
A: Ahmed → knows → Fatima (1 hop, DIRECT CONNECTION)

Q3: common-ground(Ahmed, Fatima)
A: Both connected to UET (Ahmed studies, Fatima works)


═══════════════════════════════════════════════════════════════════════════════
GRAPH BUILDING FROM NOTES
═══════════════════════════════════════════════════════════════════════════════

STEP 1: User Creates Notes

Note 1: "Ahmed and Fatima both study at UET"
Note 2: "Ahmed is a CSE student, Fatima is in EE"
Note 3: "Both attended the UET Seminar on AI"

    ↓

STEP 2: System Extracts Entities

Note 1 mentions: Ahmed, Fatima, UET
Note 2 mentions: Ahmed, Fatima, CSE, EE
Note 3 mentions: Ahmed, Fatima, Seminar, UET

    ↓

STEP 3: Create Facts from Co-mentions

From Note 1:
├─ Ahmed --knows--> Fatima (person co-mention)
├─ Ahmed --studies_at--> UET (person-place)
└─ Fatima --studies_at--> UET (person-place)

From Note 2:
├─ Ahmed --knows--> Fatima (confidence++)
└─ Ahmed --related_to--> CSE (new)

From Note 3:
├─ Ahmed --attends--> Seminar
├─ Fatima --attends--> Seminar
├─ Seminar --located_at--> UET

    ↓

STEP 4: Build Graph

Visualization:

        Ahmed ──knows──→ Fatima
         │ ↑              │ ↑
         │ │ studies_at   │ │ studies_at
         v │              v │
         UET ←──located_at─ Seminar
               attends (both)


═══════════════════════════════════════════════════════════════════════════════
PATH FINDING ALGORITHM VISUALIZATION
═══════════════════════════════════════════════════════════════════════════════

BFS (Breadth-First Search) - Shortest Path Finding:

Goal: Find shortest path from A to F

Graph:
    A ─── B ─── D
    │     │     │
    C ─── E ─── F

BFS Exploration:

Level 0:  A (start)
          │
Level 1:  B, C (neighbors of A)
          │ └─ E, D
Level 2:  D, E (neighbors of B,C)
          │ └─ F (neighbors of D,E)
Level 3:  F (FOUND!)

Shortest Path: A → B → D → F (3 hops)
Alternative: A → C → E → F (also 3 hops)


═══════════════════════════════════════════════════════════════════════════════
CONNECTED COMPONENTS VISUALIZATION
═══════════════════════════════════════════════════════════════════════════════

Your knowledge base organized into clusters:

COMPONENT 1: University Network (9 entities)
┌─────────────────────────────────────┐
│  Ahmed ────knows──── Fatima        │
│    │ studies_at       │ works_at   │
│    ↓                  ↓            │
│   UET ←─ Seminar ────→ Lib        │
│            │           │           │
│         attends      located_at    │
│            │           │           │
│         Fatima─────→ Ali (person)  │
└─────────────────────────────────────┘

COMPONENT 2: Work Network (5 entities)
┌────────────────────────┐
│  John ───colleague───→ Lisa  │
│   │ works_at           │ works_at
│   ↓                    ↓    │
│  TechCorp ←─meeting──→ Office
└────────────────────────┘

ISOLATED ENTITIES:
  Eve (no connections)
  Charlie (no connections)


═══════════════════════════════════════════════════════════════════════════════
CONFIDENCE BUILDING OVER TIME
═══════════════════════════════════════════════════════════════════════════════

Day 1:
Fact: Ahmed --studies_at--> UET
Confidence: 1
Evidence: 1 note

    Ahmed ═══1═══ UET
    
Day 2:
User writes: "Ahmed is a student at UET CS department"
Fact updated: Ahmed --studies_at--> UET
Confidence: 2
Evidence: 2 notes

    Ahmed ═══2═══ UET  (thicker line = stronger)

Day 3:
User writes: "Ahmed's GPA at UET is 3.8"
Fact updated: Ahmed --studies_at--> UET
Confidence: 3

    Ahmed ═══3═══ UET  (even stronger)

Result: High confidence relation shows in:
- Darker/thicker edges in visualizations
- Higher ranks in search results
- More prominent in path finding


═══════════════════════════════════════════════════════════════════════════════
API FLOW DIAGRAM
═══════════════════════════════════════════════════════════════════════════════

REQUEST: GET /api/relations/find-relation/person/1/person/2

    ↓

ROUTER (relations.py)
├─ Authenticate user
├─ Validate entity IDs exist
└─ Call service methods

    ↓

RELATION GRAPH SERVICE
├─ Load all facts for user
├─ Build graph structure
├─ Run BFS algorithm
│  ├─ Start from person/1
│  ├─ Explore neighbors level by level
│  └─ Return when person/2 found
├─ Run DFS algorithm (multiple paths)
├─ Find common connections
└─ Calculate confidence levels

    ↓

DATABASE QUERIES
├─ SELECT * FROM facts WHERE user_id = X
├─ SELECT * FROM persons WHERE id IN (...)
├─ SELECT * FROM places WHERE id IN (...)
└─ SELECT * FROM events WHERE id IN (...)

    ↓

RESPONSE GENERATION
├─ Convert graph objects to schemas
├─ Generate natural language summary
├─ Calculate connection strength (0-100)
└─ Serialize to JSON

    ↓

RESPONSE: RelationshipAnalysis JSON
{
  "are_directly_connected": true/false,
  "shortest_path": {...},
  "all_paths": [...],
  "common_connections": [...],
  "relation_summary": "...",
  "confidence_level": "high/medium/low"
}


═══════════════════════════════════════════════════════════════════════════════
DATA FLOW: NOTE TO FACT
═══════════════════════════════════════════════════════════════════════════════

USER ACTION:
Create note: "@p.ahmed studies at @pl.uet"

    ↓

NOTE SERVICE (existing)
├─ Parse content for @mentions
├─ Link persons, places, events
└─ Call relation_service

    ↓

RELATION SERVICE
├─ Get mentioned entities
├─ For each pair of entities:
│  ├─ Create or update fact
│  ├─ Analyze keywords for relation type
│  └─ Increase confidence if exists
└─ Store in Facts table

    ↓

DATABASE
Facts table:
┌────────┬────────┬─────────┬────────────┐
│ source │ target │ relation│ confidence │
├────────┼────────┼─────────┼────────────┤
│ Ahmed  │ UET    │studies_ │ 1          │
│        │        │ at      │            │
└────────┴────────┴─────────┴────────────┘

    ↓

NEXT TIME USER QUERIES:
GET /api/relations/neighbors/person/ahmed_id

System finds:
- Ahmed is connected to UET via studies_at (confidence: 1)
- Returns immediately from cache or fresh graph build


═══════════════════════════════════════════════════════════════════════════════
ALGORITHM COMPLEXITY COMPARISON
═══════════════════════════════════════════════════════════════════════════════

Operation                    Visual Complexity    Time      Space
──────────────────────────────────────────────────────────────────

BFS (Shortest Path)
├─ Explores level by level       ▓▓░░░░░░░░░░░░    O(V+E)    O(V)
├─ Terminates on first match
└─ Best for: Single path

DFS (Multiple Paths)
├─ Explores deeply              ▓▓▓▓░░░░░░░░░░    O(V^d)    O(d)
├─ With depth limit
└─ Best for: All paths

Union-Find (Components)
├─ Unions all pairs             ▓░░░░░░░░░░░░░    O(V+E)    O(V)
├─ Groups isolated clusters
└─ Best for: Grouping

Common Ground
├─ BFS from both sources        ▓▓░░░░░░░░░░░░    O(V+E)    O(V)
├─ Finds intersections
└─ Best for: Shared neighbors


═══════════════════════════════════════════════════════════════════════════════
RELATION TYPE HIERARCHY
═══════════════════════════════════════════════════════════════════════════════

RELATIONS
├─ Person-Place Relations
│  ├─ studies_at        (keywords: study, student, university)
│  ├─ works_at          (keywords: work, employee, job)
│  ├─ lives_at          (keywords: live, home, address)
│  ├─ visits            (keywords: visit, visit)
│  ├─ owns              (keywords: own, owner)
│  └─ manages           (keywords: manage, manager)
│
├─ Person-Event Relations
│  ├─ attends           (keywords: attend, participant)
│  ├─ organizes         (keywords: organize, organizer)
│  ├─ participates      (keywords: participate, participant)
│  └─ hosts             (keywords: host)
│
├─ Person-Person Relations
│  ├─ knows             (keywords: know, friend)
│  ├─ works_with        (keywords: work with, colleague)
│  ├─ related_to        (keywords: related, family)
│  ├─ colleague_of      (keywords: colleague)
│  ├─ supervisor_of     (keywords: supervise, manager)
│  └─ subordinate_of    (keywords: report to)
│
├─ Place-Event Relations
│  ├─ located_at        (event-place location)
│  └─ hosted_at         (event-place hosting)
│
└─ Generic
   └─ related           (unclear relation)


═══════════════════════════════════════════════════════════════════════════════
PERFORMANCE GRAPH
═══════════════════════════════════════════════════════════════════════════════

Query Time vs Entity Count:

TIME
 200ms │                                    ╱ Graph Stats
       │                                  ╱
 150ms │                                ╱
       │                          ╱─────
 100ms │              ╱──────────╱ DFS Paths
       │          ╱──╱           
  50ms │    ╱────╱ BFS Path, Common Ground
       │  ╱
   0ms └──────────────────────────────────
       10    50   100   500   1000  5000
       Entity Count (log scale)

Key Points:
- BFS is fastest (O(V+E))
- DFS slower with depth (O(V^depth))
- Most queries stay under 200ms
- Graph building is one-time cost


═══════════════════════════════════════════════════════════════════════════════
USE CASE EXAMPLE: INVESTIGATION
═══════════════════════════════════════════════════════════════════════════════

SCENARIO: Find connection between suspect A and B

KNOWLEDGE BASE:
- Suspect A was seen at Location X
- Suspect B works at Location X
- Witness C works at Location X
- Witness C is friend of Person D
- Person D was seen with Suspect B

GRAPH:
    Suspect A ──at─→ Location X ←──works_at── Suspect B
                                      │
                                   friend of
                                      ↓
                                  Witness C
                                      ↓
                                   works_at
                                      ↓
                                  Location X

QUERY: find-relation(suspect_a, suspect_b)

RESULT:
├─ Path 1: Suspect A → Location X → Suspect B (2 hops)
├─ Path 2: Suspect A → Location X → Witness C → Person D → Suspect B (4 hops)
├─ Common Ground: Location X
└─ Confidence: MEDIUM
   
INVESTIGATION INSIGHT:
"Both suspects connected to Location X. High probability of contact."


═══════════════════════════════════════════════════════════════════════════════

All diagrams are ASCII art and conceptual visualizations.
See actual response examples in RELATION_EXAMPLES.md for JSON format.
"""
