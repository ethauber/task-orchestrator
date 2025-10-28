# Task-Orchestrator

Task-Orchestrator is a local-first app that turns vague ideas into clear, actionable plans using a FastAPI backend and a Next.js frontend. It refines goals, breaks them into tasks, and generates step-by-step strategies entirely on your machine.

## Features

- **Local Execution**: Runs fully offline using [Ollama](https://ollama.com) with models like Qwen2.5 or Mistral.  
- **Refinement Flow**: `/refine`, `/breakdown`, and `/plan` endpoints guide ideas from vague to actionable.  
- **Monorepo Setup**: Unified schema between FastAPI and Next.js using shared types.  
- **Optional Persistence**: Save and load plans locally via SQLite.  

## Tech Stack

- **Backend**: Python, FastAPI, LangChain, Ollama  
- **Frontend**: React, Next.js, TypeScript  
- **Database** (optional): SQLite  

## Getting Started

### Prerequisites

- Python 3.10+  
- Node.js 18+  
- [Ollama](https://ollama.com) installed locally  
- Model pulled (for example):  
  ```bash
  ollama pull qwen2.5:7b
  ```

### Setup

```bash
# Clone repo
git clone https://github.com/ethauber/task-orchestrator.git
cd task-orchestrator

# Backend setup
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload

# Frontend setup
cd ../frontend
npm install
npm run dev
```

Then open [http://localhost:3000](http://localhost:3000) to use the app.

## API Endpoints

| Endpoint | Description |
|-----------|--------------|
| `/refine` | Clarifies vague ideas and asks follow-up questions |
| `/breakdown` | Breaks refined ideas into actionable tasks |
| `/plan` | Converts tasks into a sequenced plan with timing hints |

## Example Flow

1. Enter: *"Plan my path"*  
2. `/refine` → returns refined idea and clarifying questions  
3. `/breakdown` → returns actionable task list  
4. `/plan` → returns ordered execution plan

---

Built for local idea refinement and planning without relying on the cloud. Also, most clouds do not do this readily currently
