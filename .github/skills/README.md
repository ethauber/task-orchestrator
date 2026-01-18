# Agent Skills

This directory contains **Agent Skills**—specialized instructions that teach the AI assistant how to perform specific tasks within this codebase.

## Why use Skills?
1.  **Standardization:** Ensures complex tasks (like adding a tool or modifying a prompt) are done identically every time, following project conventions.
2.  **Context:** The AI doesn't need to "guess" where files are located or how the architecture works; the skill provides that context.
3.  **Efficiency:** Reduces the need for long, repetitive explanations in the chat.

## Available Skills

### 1. `llm-prompt-engineer`
*   **Goal:** Create or modify LLM prompts in `backend/llm/prompts/`.
*   **Usage:** "Update the plan prompt to include a risk assessment section." or "Create a new prompt for summarizing meeting notes."
*   **Behavior:** The AI will locate the JSON file, ensure strict JSON syntax, preserve placeholder variables (e.g., `{input}`), and follow the `system`/`human` message structure.

### 2. `create-tool`
*   **Goal:** Add a new function-calling tool (LangChain/MCP) to the backend.
*   **Usage:** "Create a tool to search Wikipedia." or "Add a calculator tool."
*   **Behavior:** The AI will:
    1.  Define the function with the `@tool` decorator in `backend/llm/tools_registry.py`.
    2.  Add a detailed docstring (critical for the LLM to understand how to use it).
    3.  Register the tool in the `available_tools` list in the same file.

## How to use in VS Code
When you have a request related to these topics, simply ask naturally. The "Agent Skills" feature in VS Code will automatically detect if a skill is relevant and load it.

For example:
> "I need a new tool to fetch stock prices."

The agent will load the `create-tool` skill and follow the defined procedure.
