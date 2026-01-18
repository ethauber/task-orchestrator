from typing import List, Literal, TypedDict

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
    feedback: str


prompts_ = load_prompts("plan.json")


# Nodes
async def draft_node(state: PlanState):
    """Draft a plan based on the current state"""
    steps_text = "\n".join(
        f"{i + 1}. {s.get('text', '')}" for i, s in enumerate(state["steps"])
    )

    base_prompt = prompts_["human"].format(
        optionName=state["optionName"],
        steps_block=steps_text,
        total_minutes=state["total_minutes"],
    )
    human_content = base_prompt

    if state.get("feedback"):
        print("Incorporating feedback into plan drafting.")
        human_content += (
            f"\n\nCRITIQUE FROM LAST ITERATION:\n"
            f"{state['feedback']}\n\n"
            "You must adjust the plan to resolve this feedback."
        )

    messages = [
        SystemMessage(content=prompts_["system"]),
        HumanMessage(content=human_content),
    ]

    structured_llm = base_chat_llm.with_structured_output(PlanResponse)
    response = await structured_llm.ainvoke(messages)

    return {
        "draft_plan": response,
        "iteration": state.get("iteration", 0) + 1,
        "feedback": None,
    }


async def optimize_node(state: PlanState):
    """Optimize the drafted plan using math tools and validation"""
    current_plan = state["draft_plan"]
    if not current_plan:
        return {}
    print(f"--- Optimizer Node: Normalizing Durations Iter:{state['iteration']} ---")

    # Math tool normalization calls
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

    # Validation logic
    limit = state.get("total_minutes")
    feedback = ""

    if limit is not None:
        print(f"current steps after normalization: {current_plan.steps}")
        active_minutes = sum(
            s.duration_minutes
            for s in current_plan.steps
            if not getattr(s, "parked", False)
        )
        print(f"--- Duration Check: {active_minutes} active mins vs Limit {limit} ---")

        if active_minutes > limit:
            overage = active_minutes - limit
            feedback = (
                f"CONSTRAINT VIOLATION: The active steps total {active_minutes} minutes, "
                f"which exceeds the limit of {limit} minutes by {overage} minutes. "
                f"It is not feasible to do all these steps in {limit} minutes. "
                f"You MUST set 'parked=True' for lower-priority steps until the "
                f"remaining active steps sum to {limit} or less."
            )
            print(f"--- Constraint Failed: {feedback} ---")
        else:
            print("Plan is within the time limit.")
    return {"draft_plan": current_plan, "feedback": feedback}


def should_replan(state: PlanState) -> Literal["drafter", END]:
    """Conditional edge to decide if re-drafting is needed"""
    if state["iteration"] > 3:
        print("Maximum iterations reached; ending planning.")
        return END
    if state.get("feedback", ""):
        print(f"Feedback present. {state['feedback'][:50]} re-drafting plan.")
        print(f"Current draft is: {state.get('draft_plan')}")
        return "drafter"

    print("No feedback; ending planning.")
    return END


# Create the state graph
workflow = StateGraph(PlanState)
workflow.add_node("drafter", draft_node)
workflow.add_node("optimizer", optimize_node)

workflow.set_entry_point("drafter")

workflow.add_edge("drafter", "optimizer")
# the loop to plan with state
workflow.add_conditional_edges("optimizer", should_replan)
# workflow.add_edge("optimizer", END)

plan_graph = workflow.compile()


async def plan_with_lc(req: PlanRequest) -> PlanResponse:
    """Helper to run the plan graph in a non-streaming way"""
    # Convert Pydantic steps to dicts to match PlanState definition and avoid .get() errors
    steps_as_dicts = [s.model_dump() for s in req.steps]

    initial_state = {
        "optionName": req.optionName,
        "steps": steps_as_dicts,
        "total_minutes": req.total_minutes,
        "iteration": 0,
        "draft_plan": None,
    }
    final_state = await plan_graph.ainvoke(initial_state)
    return final_state["draft_plan"]
