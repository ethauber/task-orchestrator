# builtin
from contextlib import asynccontextmanager
import json
from typing import AsyncGenerator
# third
from fastapi import Depends, FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import HttpUrl
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
# local
from backend import (
    ollama_client, settings
)
from backend.schemas import (
    Health, PingResponse, RefineRequest, RefineResponse,
    BreakdownRequest, BreakdownResponse, PlanRequest,
    PlanResponse
)
from backend.llm import math_llm
from backend.llm.tools import normalize_duration
from backend.llm.refine import refine_with_lang, chain as refine_chain
from backend.llm.breakdown import breakdown_with_lc, chain as breakdown_chain
from backend.llm.plan import plan_with_lc, plan_graph
from backend.db import engine, Base, get_db, IdeaBase


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()


app = FastAPI(
    title="task-orchestrator-backend", version="0.1.0",
    lifespan=lifespan
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def _sse_format(type_, data_):
    result = f"data: {json.dumps({'type': type_, 'data': data_})}\n\n"
    # print(f'result: {result}')
    return result


async def event_stream(chain, payload) -> AsyncGenerator[str, None]:
    """
    Create compat func for langchain events to SSE streamable
    """
    buffer = ''
    done_sent = False

    try:
        async for event in chain.astream_events(payload, version='v2'):
            kind = event['event']

            if kind == 'on_chat_model_stream':
                # print(f"{event['data']['chunk'].content}\n")
                chunk = event['data']['chunk']
                if chunk.content:
                    buffer += chunk.content
                    yield _sse_format('thinking', chunk.content)
            elif kind == 'on_chain_end' and event['name'] == 'RunnableSequence':
                final_output = event['data'].get('output')
                if final_output:
                    data_dict = final_output.model_dump()
                    print('Yielding final output from chain end... done \n\n\n\n')
                    yield _sse_format('done', data_dict)
                    done_sent = True
            elif kind == 'on_chain_end' and event['name'] == 'LangGraph':
                final_output = event['data'].get('output')
                if final_output and 'draft_plan' in final_output:
                    plan_obj = final_output['draft_plan']
                    data_dict = plan_obj.model_dump()
                    print('Yielding final output from graph end... done \n\n\n\n')
                    yield _sse_format('done', data_dict)
                    done_sent = True

        if not done_sent:
            try:
                clean = buffer.replace('```json', '').replace('```', '').strip()
                yield _sse_format('done', json.loads(clean))
            except json.JSONDecodeError:
                yield _sse_format('type', buffer)
    except Exception as catchall_e:
        print(f'Caught exception in event_stream: {catchall_e}')
        yield _sse_format('error', str(catchall_e))


@app.post('/stream/refine')
async def stream_refine(request: RefineRequest):
    """Streaming refine using existing LangChain setup"""
    payload = {'idea': request.idea, 'context': request.context}
    return StreamingResponse(event_stream(refine_chain, payload))


@app.post('/stream/breakdown')
async def stream_breakdown(request: BreakdownRequest):
    """Stream breakdown with existing lang setup"""
    return StreamingResponse(event_stream(breakdown_chain, {
        'definition': request.definition, 'max_steps': request.max_steps
    }))


@app.post('/stream/plan')
async def stream_plan(request: PlanRequest):
    """Stream plan with existing lang setup"""
    steps_as_dicts = [s.model_dump() for s in request.steps]

    return StreamingResponse(event_stream(plan_graph, {
        'optionName': request.optionName,
        'steps': steps_as_dicts,
        'total_minutes': request.total_minutes,
        'iteration': 0,
        'draft_plan': None
    }))


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
async def plan(req: PlanRequest):
    try:
        out = await plan_with_lc(req)
        if out:
            out.parked_indices = [i + 1 for i, s in enumerate(out.steps) if s.parked]
            out.total_duration = sum(
                s.duration_minutes for s in out.steps if not s.parked)
        return out
    except Exception as general_exception:
        raise HTTPException(
            status_code=502, detail=f'plan failed with\n{general_exception}'
        )


@app.post("/test-db")
async def test_db_connection(
    request: RefineRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Simple endpoint to verify DB writes and reads.
    """
    new_idea = IdeaBase(
        initial=request.idea,
        refined=f"Processed: {request.idea}",
        steps="[]"
    )

    db.add(new_idea)
    await db.commit()
    await db.refresh(new_idea)

    result = await db.execute(select(IdeaBase).where(IdeaBase.id == new_idea.id))
    saved_idea = result.scalar_one_or_none()
    if not saved_idea:
        raise HTTPException(
            status_code=500, detail="Failed to retrieve the saved idea from DB."
        )

    return {
        "status": "success",
        "db_record": {
            "id": saved_idea.id,
            "initial": saved_idea.initial,
            "created_at": saved_idea.created_at
        }
    }


@app.post("/tools/test-math")
async def test_tool_binding(raw_minutes: int):
    """
    Tests if the existing LLM instance can correctly bind and call
    the normalize_duration tool.
    """
    msg = f"Normalize a duration of {raw_minutes} minutes."
    response = await math_llm.ainvoke(msg)

    if response.tool_calls:
        tool_call = response.tool_calls[0]  # Grab the first tool decision
        tool_args = tool_call['args']       # e.g., {'minutes': 23}

        # Invoke the python function using the args the LLM gave us
        result = normalize_duration.invoke(tool_args)

        return {
            "status": "success",
            "original_input": raw_minutes,
            "tool_selected": tool_call['name'],
            "llm_generated_args": tool_args,
            "final_result": result
        }

    return {
        "status": "missed_tool_call",
        "llm_response": response.content
    }
