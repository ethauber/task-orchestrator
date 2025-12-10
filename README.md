
![anim-50pct-64c](https://github.com/user-attachments/assets/b491d048-a898-4ed7-818f-103cf544eea1)

# Task-Orchestrator

Task-Orchestrator is a local-first app that turns vague ideas into clear, actionable plans using a FastAPI backend and a Next.js frontend. It refines goals, breaks them into tasks, and generates step-by-step strategies entirely on your machine.

## Features

- **Local Execution**: Runs LLM ops fully offline using [Ollama](https://ollama.com). Currently model is defaulted to Qwen2.5.  
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
| `/breakdown` | Breaks refined ideas into actionable tasks |  ⚙️ Minimal ready |
| `/plan` | Converts tasks into a sequenced plan with timing hints |  ⚙️ Minimal ready |

## Example Flow

1. Enter: *"Plan my path"*  
2. `/refine` → returns refined idea and clarifying questions  
3. `/breakdown` → returns actionable task list  
4. `/plan` → returns ordered execution plan

## MCP Server

This project exposes its functionality via the [Model Context Protocol (MCP)](https://modelcontextprotocol.io/), allowing AI assistants (like Claude Desktop) to interact with the task orchestrator directly.

### 1. Identify your Virtual Environment Path
External tools often don't have the same `PATH` as your terminal, so `poetry` might not be found. It is most robust to use the absolute path to the Python executable in your virtual environment.

Run this command to find your environment path:
```bash
poetry env info --path
```
*Example output: `/Users/username/Library/Caches/pypoetry/virtualenvs/task-orchestrator-XXXXXX-py3.11`*

Append `/bin/python` to this path to get your executable.

### 2. Configure Claude Desktop

Add the following to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "task-orchestrator": {
      "command": "/ABSOLUTE/PATH/TO/VIRTUALENV/bin/python",
      "args": ["/ABSOLUTE/PATH/TO/task-orchestrator/mcp_entry.py"],
      "cwd": "/ABSOLUTE/PATH/TO/task-orchestrator"
    }
  }
}
```

*   **command**: The full path you found in Step 1 (ending in `/bin/python`).
*   **args**: The **absolute path** to the `mcp_entry.py` file in your project root.
*   **cwd**: The full path to where you cloned this repository.

### Manual Run (Testing)
You can still run it manually in your terminal if needed:
```bash
poetry run python mcp_entry.py
```

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
