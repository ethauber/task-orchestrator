import os

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import HttpUrl

from backend.schemas import Health, PingResponse, RefineRequest, RefineResponse
from backend.llm_refine import refine_with_lang

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


@app.get("/health", response_model=Health)
def health():
    return Health(
        status="ok", model=MODEL_NAME,
        ollama_url=HttpUrl(OLLAMA_BASE_URL)
    )


@app.get("/llm/ping", response_model=PingResponse)
def llm_ping():
    if ollama is None:
        raise HTTPException(status_code=500, detail="ollama client unavailable")

    try:
        # Interesting if a word close in vector space like GRID
        # is chosen then it only replies with WAFFLES qwen2.5
        r = ollama.generate(
            model=MODEL_NAME, prompt="Flip a coin to pick 'WAFFLES' or 'OK' then reply"
            " with it. Only respond with the outcome"
        )
        return PingResponse(response=r["response"].strip())
    except Exception as general_exception:
        raise HTTPException(status_code=502, detail=f"ollama error: {general_exception}")


@app.post("/refine", response_model=RefineResponse)
def refine(request: RefineRequest):
    if ollama is None:
        raise HTTPException(status_code=500, detail="ollama client unavailable")

    try:
        out = refine_with_lang(request)
        return out
    except Exception as gen_exception:
        raise HTTPException(502, detail=f'refine failed with\n{gen_exception}')
