
![anim-50pct-64c](https://github.com/user-attachments/assets/b491d048-a898-4ed7-818f-103cf544eea1)

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

- Python 3.10+ (3.11.13)  
- Poetry for dependency management (2.2.1)  
- Node.js 18+ (v22.20.0)  
- npm (10.9.3)  
- npx (10.9.3)  
- [Ollama](https://ollama.com) installed locally (0.12.5)  
- Server Started in one terminal and Model pulled in another (for example):  
  ```zsh
  ollama serve
  ```
  ```bash
  ollama pull qwen2.5:7b
  ```

### Setup
#### Pre-requistites (MacOS example) 
```bash
# Install Homebrew
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Python
brew install python

# Install Node.js
brew install node

# Install Poetry
curl -sSL https://install.python-poetry.org | python3 -

# Install ollama
curl -fsSL https://ollama.com/install.sh | sh

# Optional diagramming tools
brew install graphviz
npm install -g @mermaid-js/mermaid-cli

# Creating scaffolding for Next.js (React)
npx create-next-app@latest frontend --ts --eslint --app --src-dir --import-alias "@/*"
```

#### Run Application
```bash
# Clone repo
git clone https://github.com/ethauber/task-orchestrator.git
cd task-orchestrator

# Backend setup
poetry init
poetry install
poetry run python -m uvicorn main:app --reload

# Frontend setup
cd ../frontend
npm install
npm run dev
```

Then open [http://localhost:3000](http://localhost:3000) to use the app.

## API Endpoints

| Endpoint | Description | Status |
|-----------|--------------|---|
| `/refine` | Clarifies vague ideas and asks follow-up questions | ⚙️ Minimal ready |
| `/breakdown` | Breaks refined ideas into actionable tasks | 🚧 In progress |
| `/plan` | Converts tasks into a sequenced plan with timing hints | 🚧 In progress |

## Example Flow

1. Enter: *"Plan my path"*  
2. `/refine` → returns refined idea and clarifying questions  
3. `/breakdown` → returns actionable task list  
4. `/plan` → returns ordered execution plan

---

Built for local idea refinement and planning without relying on the cloud. Also, most clouds do not do this readily currently


#### Collection of links
```
https://docs.ollama.com/linux
https://mermaid.js.org/intro/
https://python-poetry.org/docs/basic-usage/
https://fastapi.tiangolo.com/
https://docs.langchain.com/oss/python/langchain/overview#install

https://docs.langchain.com/oss/python/integrations/providers/ollama
https://docs.ollama.com/capabilities/streaming
https://reference.langchain.com/python/integrations/langchain_ollama/#langchain_ollama.ChatOllama.astream


```
