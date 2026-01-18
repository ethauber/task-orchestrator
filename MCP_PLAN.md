# MCP Integration Plan

## Objective
Enable external AI assistants (like Claude Desktop or IDEs) to directly utilize the Task Orchestrator's core logic—refining ideas, breaking them down, and generating plans—by implementing the Model Context Protocol (MCP).

## 1. Architecture Design
*   **Server Type**: Use `FastMCP` (from the `mcp` python SDK) for a lightweight, decorator-based implementation.
*   **Location**: Create a new entry point `backend/mcp_server.py`.
*   **Integration Point**: The MCP server will import directly from `backend.llm` and `backend.schemas` to reuse existing business logic, ensuring the CLI/MCP behavior matches the HTTP API exactly.

## 2. Tools to Expose
We will map the existing internal functions to MCP Tools.

| MCP Tool Name | Underlying Function | Inputs | Description |
| :--- | :--- | :--- | :--- |
| `refine_idea` | `refine_with_lang` | `idea` (str), `context` (str) | Takes a raw idea + context, returns a refined goal and questions. |
| `breakdown_task` | `breakdown_with_lc` | `definition` (str), `max_steps` (int) | Takes a definition, returns "Lean" and "Thorough" options. |
| `generate_plan` | `plan_with_lc` | `option_name` (str), `steps` (List[str]), `total_minutes` (int) | Takes specific steps + time constraint, returns a scheduled plan with dependencies. |
| `normalize_minutes`| `normalize_duration` | `minutes` (int) | Utility to round time durations (useful for LLMs doing math). |

## 3. Implementation Steps
1.  **Dependencies**: Add `mcp` to `pyproject.toml` via Poetry.
2.  **Server Code**:
    *   Initialize `FastMCP("Task Orchestrator")`.
    *   Create wrappers for async functions.
    *   Ensure Pydantic models are serialized to JSON strings for MCP compatibility, as MCP tools primarily consume/return primitive types or JSON strings.
3.  **Verification**: Create a script `verify_mcp.py` to programmatically load the server and list available tools to ensure they registered correctly.
4.  **Documentation**: Update `README.md` with specific configuration blocks for `claude_desktop_config.json`.

## 4. Usage
To run the server:
```bash
poetry run python -m backend.mcp_server
```

To configure in Claude Desktop:
```json
{
  "mcpServers": {
    "task-orchestrator": {
      "command": "poetry",
      "args": ["run", "python", "-m", "backend.mcp_server"],
      "cwd": "/path/to/project"
    }
  }
}
```
