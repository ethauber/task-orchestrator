from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os

from dotenv import load_dotenv
load_dotenv()

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
MODEL_NAME = os.getenv("MODEL_NAME", "qwen2.5:7b")

# lazy-init ollama client
try:
    from ollama import Client
    ollama = Client(host=OLLAMA_BASE_URL)
except Exception as ollama_init_error:
    print(f"Warning: could not initialize ollama client at {OLLAMA_BASE_URL}\n{ollama_init_error}")
    ollama = None


app = FastAPI(title="task-orchestrator-backend", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://0.0.0.0:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class Health(BaseModel):
    status: str
    model: str
    ollama_url: str


class PingResponse(BaseModel):
    response: str


@app.get("/health", response_model=Health)
def health():
    return Health(status="ok", model=MODEL_NAME, ollama_url=OLLAMA_BASE_URL)


@app.get("/llm/ping", response_model=PingResponse)
def llm_ping():
    if ollama is None:
        raise HTTPException(status_code=500, detail="ollama client unavailable")

    try:
        r = ollama.generate(model=MODEL_NAME, prompt="Reply with OK")
        return PingResponse(response=r["response"].strip())
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"ollama error: {e}")
