from typing import List, TypedDict

from langchain_core.messages import SystemMessage, HumanMessage
from langgraph.graph import StateGraph, END

from backend.llm import base_chat_llm, math_llm, load_prompts
from backend.llm.tools import normalize_duration
from backend.schemas import PlanRequest, PlanResponse


# State Definition required for planning pattern
class PlanState(TypedDict):
    optionName: str
    steps: List[dict]
    total_minutes: int
    draft_plan: PlanResponse | None
    iteration: int


prompts_ = load_prompts("plan.json")


# Nodes
async def draft_node(state: PlanState):
    steps_text = "\n".join(
        f'{i+1}. {s.get("text", "")}' for i, s in enumerate(state["steps"])
    )

    messages = [
        SystemMessage(content=prompts_["system"]),
        HumanMessage(
            content=prompts_["human"].format(
                optionName=state["optionName"],
                steps_block=steps_text,
                total_minutes=state["total_minutes"],
            )
        ),
    ]

    structured_llm = base_chat_llm.with_structured_output(PlanResponse)
    response = await structured_llm.ainvoke(messages)

    return {"draft_plan": response, "iteration": state.get("iteration", 0) + 1}


async def optimize_node(state: PlanState):
    current_plan = state["draft_plan"]
    if not current_plan:
        return {}

    batch_prompts = [
        [
            HumanMessage(
                content=f"Normalize a duration of {step.duration_minutes} minutes."
            )
        ]
        for step in current_plan.steps
    ]

    results = await math_llm.abatch(batch_prompts)

    updated_steps = []
    for step, response in zip(current_plan.steps, results):
        if response.tool_calls:
            call = response.tool_calls[0]
            new_val = normalize_duration.invoke(call["args"])
            step.duration_minutes = new_val
        updated_steps.append(step)

    current_plan.steps = updated_steps
    return {"draft_plan": current_plan}


# Create the state graph
workflow = StateGraph(PlanState)
workflow.add_node("drafter", draft_node)
workflow.add_node("optimizer", optimize_node)

workflow.set_entry_point("drafter")
workflow.add_edge("drafter", "optimizer")
workflow.add_edge("optimizer", END)

plan_graph = workflow.compile()


async def plan_with_lc(req: PlanRequest) -> PlanResponse:
    """Helper to run the plan graph in a non-streaming way"""
    initial_state = {
        "optionName": req.optionName,
        "steps": req.steps,
        "total_minutes": req.total_minutes,
        "iteration": 0,
        "draft_plan": None,
    }
    final_state = await plan_graph.ainvoke(initial_state)
    return final_state["draft_plan"]
