# Knowledge Base System with Relationship Discovery

## Overview
An intelligent knowledge management system using advanced DSA concepts for relationship discovery, temporal querying, and version control.

## Tech Stack
- **Frontend**: React, TypeScript, TailwindCSS, Vite
- **Backend**: Python, FastAPI, SQLAlchemy
- **Database**: PostgreSQL
- **Key DSA**: Graphs, Tries, Segment Trees, Merkle Trees, Union-Find

## Setup Instructions

### Prerequisites
- Node.js 18+
- Python 3.11+
- PostgreSQL 15+

### Backend Setup (PowerShell)
Use the helper scripts from the project root to create the virtual environment and run the backend.

```powershell
.\scripts\setup-backend.ps1
.\scripts\run-backend.ps1
```

### Frontend Setup (PowerShell)
Use the helper scripts from the project root to install dependencies and start the dev server.

```powershell
.\scripts\setup-frontend.ps1
.\scripts\run-frontend.ps1
```

## Project Structure
- `/frontend` - React TypeScript application
- `/backend` - FastAPI Python backend
- `/docs` - Project documentation

## Features
- Intelligent note-taking with @mentions
- Relationship discovery using graph algorithms
- Complex temporal queries
- Version control with efficient diffing
- Knowledge graph visualization

## DSA Implementations
- Graph (BFS, DFS, Dijkstra, SCC)
- Trie (Autocomplete)
- Segment Tree (Temporal queries)
- Merkle Tree (Version control)
- Union-Find (Clustering)
- Inverted Index (Search)
- LCS (Text diffing)

## License
MIT

Notes:
- The backend will bind to `http://0.0.0.0:8000` and exposes a health route at `/api/health`.
- The frontend uses Vite; the dev server default port is `5173`. If your browser opens a different port, check the terminal output from `npm run dev`.
