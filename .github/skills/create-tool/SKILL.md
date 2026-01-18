# Skill: Create Tool

## Description
This skill guides the creation and registration of new LangChain/MCP tools in the `backend/llm/tools_registry.py` file.

## Context
*   **Registry File:** `backend/llm/tools_registry.py`
*   **Framework:** LangChain (`@tool` decorator).
*   **Purpose:** These tools are bound to the LLM agent to allow it to perform actions (search, calculation, API calls).

## Rules
1.  **Imports:** Ensure `from langchain_core.tools import tool` is imported.
2.  **Decorator:** Decorate the function with `@tool`.
3.  **Docstring:** Write a descriptive docstring. **This is the prompt for the LLM.** It must explain *what* the tool does and *when* to use it.
4.  **Type Hints:** Use Python type hints for all arguments and the return value.
5.  **Registration:** Add the function name to the `available_tools` list at the bottom of the file.

## Procedure
1.  **Read:** Read `backend/llm/tools_registry.py` to see existing imports and tools.
2.  **Implement:** Append the new tool function to the file.
3.  **Register:** Update the `available_tools = [...]` list to include the new function.

## Example

```python
@tool
def get_weather(city: str) -> str:
    """
    Get the current weather for a specific city.
    Use this when the user asks about weather conditions.
    """
    # Implementation...
    return "Sunny"

# ... existing code ...

available_tools = [web_search, calculator, get_weather]
```
