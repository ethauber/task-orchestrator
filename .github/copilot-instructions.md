# Copilot Repository Instructions

## Project Overview

Task-Orchestrator is a local-first application that turns vague ideas into clear, actionable plans. It combines a FastAPI backend with a Next.js frontend to refine goals, break them into tasks, and generate step-by-step strategies entirely on the user's machine.

**Tech Stack:**
- **Backend**: Python 3.10+ (tested with 3.11.13), FastAPI, LangChain, Ollama, SQLAlchemy
- **Frontend**: React, Next.js, TypeScript
- **Database**: SQLite (optional persistence)
- **Package Management**: Poetry (backend), npm (frontend)
- **LLM Runtime**: Ollama (local model execution, default: Qwen2.5:7b)

## Prerequisites

- Python 3.10+ (tested with 3.11.13)
- Poetry 2.2.1+
- Node.js 18+ (tested with v22.20.0)
- npm 10.9.3+
- Ollama 0.12.5+ (with `ollama serve` running and model pulled)

## Build and Test Commands

### Backend
```bash
# Install dependencies
poetry install

# Run backend server
poetry run uvicorn backend.main:app --reload --port 8000

# Run tests
poetry run pytest

# Database migrations
poetry run alembic revision --autogenerate -m "description"
poetry run alembic upgrade head
```

### Frontend
```bash
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev

# Build for production
npm run build

# Lint code
npm run lint
```

### Full Application
```bash
# Run all services (LLM, backend, frontend) concurrently
npm run dev

# Kill all ports if needed
npm run kill-ports
```

## Coding Standards

### Python (Backend)

- Use **type hints** for all function parameters and return values
- Follow **PEP 8** style guidelines
- Organize imports in order: builtin, third-party, local (with comments `# builtin`, `# third`, `# local`)
- Use **Pydantic models** for request/response validation (see `backend/schemas.py`)
- Use **async/await** for all database operations and I/O
- Database sessions should use `AsyncSession` with proper dependency injection via `get_db()`
- Use **SQLAlchemy 2.0+ style** queries (e.g., `select()` statements)
- Follow the existing pattern for API endpoints in `backend/main.py`

**Example (Good):**
```python
# builtin
from typing import AsyncGenerator

# third
from fastapi import Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

# local
from backend.schemas import RefineRequest, RefineResponse
from backend.db import get_db

async def refine_endpoint(
    request: RefineRequest,
    db: AsyncSession = Depends(get_db)
) -> RefineResponse:
    ...
```

### TypeScript (Frontend)

- Use **TypeScript** for all source files
- Prefer **functional components** with React hooks
- Use **named exports** over default exports
- Keep shared types in `frontend/src/lib/types.ts` and sync with backend schemas
- Follow Next.js 14+ App Router conventions
- Use the `@/*` import alias for internal imports

**Example (Good):**
```typescript
export interface RefineRequest {
  initialIdea: string;
}

export const RefineForm: React.FC = () => {
  ...
}
```

## Architecture and Patterns

### Backend Flow
1. **Refine** (`/refine`): Clarifies vague ideas and asks follow-up questions
2. **Breakdown** (`/breakdown`): Breaks refined ideas into actionable task options
3. **Plan** (`/plan`): Converts selected tasks into a sequenced plan with timing

### MCP Server
- The project exposes functionality via Model Context Protocol (MCP)
- Entry point: `mcp_entry.py`
- Requires absolute paths for Claude Desktop configuration
- Uses Poetry virtual environment Python executable

### Database Migrations
- Use **Alembic** for all schema changes
- Always autogenerate migration scripts: `poetry run alembic revision --autogenerate -m "description"`
- **Important**: When updating backend models, sync corresponding TypeScript types in `frontend/src/lib/types.ts`

## Testing Conventions

- Backend tests use **pytest** with **TestClient** from FastAPI
- Mock external dependencies (like Ollama LLM calls) using `unittest.mock`
- Tests are in the `tests/` directory
- Follow the pattern in `tests/test_backend.py` for new tests

## Workflow Rules

- Use meaningful commit messages
- Keep changes minimal and focused
- Ensure all tests pass before committing
- For schema changes, remember to sync backend and frontend types

## Restrictions

**Must NOT:**
- Modify or commit files in `/node_modules`, `/.next`, `/build`, `/__pycache__`, or `/.venv`
- Commit secrets, API keys, or credentials
- Modify `.git` directory contents
- Change Ollama model configuration without updating documentation
- Remove or modify working code unless fixing a bug or vulnerability
- Break existing API contracts without updating both backend and frontend

**Must:**
- Use async patterns for all I/O operations
- Properly close database sessions
- Handle errors gracefully with appropriate HTTP status codes
- Validate all user inputs using Pydantic models
- Keep frontend types synchronized with backend schemas

## Key Files and Directories

- `backend/main.py` - FastAPI application and endpoints
- `backend/schemas.py` - Pydantic models for API requests/responses
- `backend/db.py` - Database models and session management
- `backend/llm/` - LangChain integration and LLM logic
- `frontend/src/lib/types.ts` - Shared TypeScript types
- `mcp_entry.py` - MCP server entry point
- `alembic/` - Database migration scripts
- `tests/` - Backend tests

## Additional Notes

- The application is designed to run **fully offline** using local Ollama models
- CORS is configured to allow frontend-backend communication
- Database is created automatically on application startup via lifespan context manager
- Use `poetry env info --path` to find the virtual environment path for MCP configuration
