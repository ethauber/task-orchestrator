# builtin
import json
from typing import AsyncGenerator
# third
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import HttpUrl
# local
from backend import (
    ollama_client, settings
)
from backend.schemas import (
    Health, PingResponse, RefineRequest, RefineResponse,
    BreakdownRequest, BreakdownResponse, PlanRequest,
    PlanResponse
)
from backend.llm.refine import refine_with_lang, chain as refine_chain
from backend.llm.breakdown import breakdown_with_lc
from backend.llm.plan import plan_with_lc


app = FastAPI(title="task-orchestrator-backend", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


async def stream_json_response(chain, input_data: dict) -> AsyncGenerator[str, None]:
    """
    Stream LangChain output as SSE
    Accumulates chuns into valid JSON at the end
    """
    content_buffer = ""
    try:
        async for chunk in chain.astream(input_data):
            if hasattr(chunk, 'content'):
                text = chunk.content
            elif isinstance(chunk, str):
                text = chunk
            else:
                text = str(chunk)

            content_buffer += text

            yield f"data: {json.dumps({'type': 'content', 'data': text})}\n\n"

        try:
            print(f'Non CLEANED {content_buffer}')
            clean = content_buffer.replace('```json', '').replace('```', '').strip()
            print(f'CLEANED {clean}')
            final = json.loads(clean)
            yield f"data: {json.dumps({'type': 'done', 'data': final})}\n\n"
        except json.JSONDecodeError:
            yield f"data: {json.dumps({'type': 'done', 'data': content_buffer})}\n\n"
    except Exception as catchall_exception:
        yield f"data: {json.dumps({'type': 'error', 'data': str(catchall_exception)})}"
        "\n\n"


@app.post('/stream/refine')
async def stream_refine(request: RefineRequest):
    """Streaming refine using existing LangChain setup"""
    return StreamingResponse(stream_json_response(
        refine_chain, {'idea': request.idea, 'context': request.context})
    )


@app.get("/health", response_model=Health)
def health():
    return Health(
        status="ok", model=settings.model_name or '',
        ollama_url=HttpUrl(settings.ollama_base_url or '')
    )


@app.get("/llm/ping", response_model=PingResponse)
def llm_ping():
    if ollama_client is None:
        raise HTTPException(status_code=500, detail="ollama client unavailable")

    try:
        # Interesting if a word close in vector space like GRID
        # as opposed to OK is the other option
        # then it only replies with WAFFLES qwen2.5
        r = ollama_client.generate(
            model=settings.model_name or '',
            prompt="Flip a coin to pick 'WAFFLES' or 'OK' then reply"
            " with it. Only respond with the outcome"
        )
        return PingResponse(response=r["response"].strip())
    except Exception as general_exception:
        raise HTTPException(status_code=502, detail=f"ollama error: {general_exception}")


@app.post("/refine", response_model=RefineResponse)
def refine(request: RefineRequest):
    if ollama_client is None:
        raise HTTPException(status_code=500, detail="ollama client unavailable")

    try:
        out = refine_with_lang(request)
        return out
    except Exception as gen_exception:
        raise HTTPException(502, detail=f'refine failed with\n{gen_exception}')


@app.post('/breakdown', response_model=BreakdownResponse)
def breakdown(req: BreakdownRequest):
    try:
        out = breakdown_with_lc(req)
        for p in out.plans:
            p.name = (p.name or '').strip() or 'Plan'
            p.steps = [
                s for s in p.steps if s.text.strip()][: min(
                    len(p.steps), req.max_steps or 7)
            ]
            return out
    except Exception as general_exception:
        raise HTTPException(
            status_code=502, detail=f'breakdown failed with\n{general_exception}'
        )


@app.post('/plan', response_model=PlanResponse)
def plan(req: PlanRequest):
    try:
        out = plan_with_lc(req)
        # until tool calling is implemented force 15 min multiples old fashioned way
        for s in out.steps:
            q = int(round(s.duration_minutes / 15.0)) * 15
            s.duration_minutes = 15 if q < 15 else q

        out.parked_indices = [i + 1 for i, s in enumerate(out.steps) if s.parked]
        out.total_duration = sum(s.duration_minutes for s in out.steps if not s.parked)
        return out
    except Exception as general_exception:
        raise HTTPException(
            status_code=502, detail=f'plan failed with\n{general_exception}'
        )
