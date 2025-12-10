import os
import sys
from dotenv import load_dotenv

# Load environment variables explicitly
# We need to find the .env file relative to this script
current_dir = os.path.dirname(os.path.abspath(__file__))
dotenv_path = os.path.join(current_dir, '.env')
load_dotenv(dotenv_path)

from mcp.server.fastmcp import FastMCP
from typing import List, Optional

from backend.llm.refine import refine_with_lang
from backend.llm.breakdown import breakdown_with_lc
from backend.llm.plan import plan_with_lc
from backend.llm.tools import normalize_duration as normalize_duration_tool
from backend.schemas import RefineRequest, BreakdownRequest, PlanRequest, PlanStep


mcp = FastMCP("Task Orchestrator")


@mcp.tool()
def refine_idea(idea: str, context: Optional[str] = None) -> str:
    """
    Refines a raw idea into a clearer, more structured concept using an LLM.
    Returns a JSON string with the refined idea and clarifying questions.
    """
    req = RefineRequest(idea=idea, context=context)
    result = refine_with_lang(req)
    return result.model_dump_json()


@mcp.tool()
def breakdown_task(definition: str, max_steps: int = 5) -> str:
    """
    Breaks down a task definition into two alternative plans (Lean and Thorough).
    Returns a JSON string containing the plans.
    """
    req = BreakdownRequest(definition=definition, max_steps=max_steps)
    result = breakdown_with_lc(req)
    return result.model_dump_json()


@mcp.tool()
async def generate_plan(option_name: str, steps: List[str], total_minutes: int) -> str:
    """
    Generates a detailed schedule for a list of steps within a time limit.

    Args:
        option_name: Name of the plan option (e.g., 'Lean Plan')
        steps: List of step descriptions (strings)
        total_minutes: Total time budget in minutes

    Returns:
        JSON string containing the finalized plan with durations and dependencies.
    """
    # Convert string steps to PlanStep objects
    plan_steps = [PlanStep(text=s) for s in steps]

    req = PlanRequest(
        optionName=option_name, steps=plan_steps, total_minutes=total_minutes
    )

    result = await plan_with_lc(req)
    if result:
        return result.model_dump_json()
    return "{}"


@mcp.tool()
def normalize_minutes(minutes: int) -> int:
    """
    Rounds a duration to the nearest 15-minute increment (min 15).
    """
    return normalize_duration_tool.invoke({"minutes": minutes})


if __name__ == "__main__":
    print("Starting MCP server...")
    mcp.run()
    print("MCP server stopped.")
