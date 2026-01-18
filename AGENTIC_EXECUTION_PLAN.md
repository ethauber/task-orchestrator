# Implementation Plan: Autonomous Step Execution

This plan details the steps to transform the Task Orchestrator from a passive planner into an active agent capable of executing tasks using local tools and web search.

## Phase 0: Prerequisites

### 0.1 Dependencies
*   **Goal:** Install necessary libraries for tools and search.
*   **Command:** `poetry add langchain-community duckduckgo-search`
*   **Verification:** Check `pyproject.toml` to ensure packages are listed.

## Phase 1: Backend Architecture (LangGraph + Tools)

### 1.1 Tool Registry Setup
*   **Goal:** Create a modular registry of tools the LLM can invoke.
*   **File:** `backend/llm/tools_registry.py` (New File)
*   **Tools:**
    *   `web_search`: Wraps `DuckDuckGoSearchRun` (from `langchain_community`).
    *   `calculator`: Simple python evaluation or `llm_math`.
    *   `safe_writer`: (Optional initial file writer, strictly scoped).

### 1.2 Agent Graph Definition
*   **Goal:** Create a specialized LangGraph for single-step execution.
*   **File:** `backend/llm/executor.py` (New File)
*   **Architecture:**
    *   **State:** `AgentState` TypedDict with `messages` (list) and `outcome` (str).
    *   **Nodes:**
        *   `call_model`: Calls LLM (bound with tools).
        *   `call_tool`: Executes the chosen tool(s).
    *   **Logic:** Conditional edge `should_continue` checks for tool calls.
    *   **Helper Function:** `execute_step_stream(step_text, plan_context, prev_result)`
        *   Constructs initial prompts (System: "You are an executor...", User: Step details).
        *   Invokes `executor_graph.astream_events` (v2) with this initial state.
        *   Yields raw events to be processed by the API for granular updates.

### 1.3 Request Schema
*   **Goal:** Define the data contract for the execution endpoint.
*   **File:** `backend/schemas.py`
*   **New Models:**
    *   `StepExecutionRequest`:
        *   `step_text` (str): The specific action to take.
        *   `plan_context` (str): Surrounding plan context (e.g., "Step 3 of 'Trip to Kyoto'").
        *   `prev_step_result` (Optional[str]): Result from a previous step if chained.

### 1.4 API Endpoint
*   **Goal:** Expose the agent via a streaming endpoint.
*   **File:** `backend/main.py`
*   **Route:** `POST /stream/execute_step`
*   **Logic:**
    *   Call `execute_step_stream`.
    *   Iterate over the generator and map events to SSE:
        *   `on_chat_model_stream` -> `event: thinking` (content chunk)
        *   `on_tool_start` -> `event: tool_call` (tool name and input args)
        *   `on_tool_end` -> `event: tool_result` (tool output)
        *   `on_chain_end` (for the final graph output) -> `event: final_result`

## Phase 2: Frontend UX (Interactive Execution)

### 2.1 Types & API
*   **Goal:** Update types and API client to handle the new stream.
*   **File:** `frontend/src/lib/types.ts`
    *   Add `StepExecutionRequest` interface matching the backend Pydantic model.
*   **File:** `frontend/src/lib/api.ts`
    *   Add `executeStep` function supporting the specific SSE event types.

### 2.2 Component: `StepExecutor`
*   **Goal:** A UI component to visualize the agent's progress.
*   **File:** `frontend/src/components/StepExecutor.tsx` (New File)
*   **Features:**
    *   **State:** Manage `logs` array (for thoughts/tools) and `result` string.
    *   **UI:** Collapsible "Logs" section (shows "Searching web for...", "Calculating...").
    *   **Result:** Markdown rendering for the final result.
    *   **Status:** Indicators (Idle, Running, Success, Error).

### 2.3 Integration into `BreakdownPage`
*   **Goal:** Embed the executor into the Final Plan list.
*   **File:** `frontend/src/app/breakdown/page.tsx`
*   **Action:**
    *   Update the `Final Plan` rendering loop.
    *   Add a "Run" button to each step that isn't parked.
    *   When clicked, replace/append the `StepExecutor` component to that list item.

## Phase 3: Testing & Verification

### 3.1 Backend Tests
*   **File:** `tests/test_executor.py` (New File)
*   **Tests:**
    *   Mock `DuckDuckGoSearch` to verify graph transitions (Reason -> Tool -> Reason -> End).
    *   Verify SSE stream format matches frontend expectations.

### 3.2 Manual Verification
*   **Scenario:**
    1.  Generate a plan: "Plan a weekend trip to Kyoto."
    2.  Step 1: "Check weather in Kyoto for next weekend." -> Click "Run".
    3.  **Expectation:** Agent searches web, sees forecast, returns summary ("It will be sunny, 22°C...").

## Dependencies
*   `langchain-community` (for tools)
*   `duckduckgo-search` (for search provider)
*   `langgraph` (existing)
*   `ollama` (existing)
