from typing import List, Literal, TypedDict, Optional
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import BaseMessage, HumanMessage, ToolMessage
from langchain_core.runnables import RunnableConfig
from langchain_ollama import ChatOllama
from langgraph.graph import END, StateGraph, START

from backend import settings
from backend.llm.tools_registry import available_tools


# --- 1. Define Graph State ---
class AgentState(TypedDict):
    messages: List[BaseMessage]
    # The outcome of the execution, if available
    outcome: Optional[str]


# --- 2. Initialize LLM and Tools ---
# Use the same ollama client setup as the rest of the backend
llm = ChatOllama(
    model=settings.model_name or "qwen2.5:7b",
    temperature=0.0,  # Agents usually prefer lower temperature
    base_url=str(settings.ollama_base_url) if settings.ollama_base_url else None,
)

# Bind tools to the LLM
# This makes the LLM aware of the tools and their schemas
llm_with_tools = llm.bind_tools(available_tools)

# --- 3. Define Nodes ---


# Node 1: Call the LLM to decide what to do
async def call_model(state: AgentState, config: RunnableConfig):
    messages = state["messages"]
    # print(f"--- Agent calling model with messages: {messages}")
    response = await llm_with_tools.ainvoke(messages, config)
    # print(f"--- Agent model response: {response}")
    return {"messages": [response]}


# Node 2: Call the tool if the LLM decided to
async def call_tool(state: AgentState, config: RunnableConfig):
    messages = state["messages"]
    last_message = messages[-1]

    # print(f"--- Agent calling tool for message: {last_message}")

    tool_outputs = []
    # Ensure tool_calls is iterable
    if not hasattr(last_message, "tool_calls") or not last_message.tool_calls:
        return {"messages": []}

    for tool_call in last_message.tool_calls:
        tool_name = tool_call["name"]
        tool_args = tool_call["args"]

        # Find the tool in our registry
        chosen_tool = next((t for t in available_tools if t.name == tool_name), None)
        if chosen_tool:
            try:
                # print(f"--- Executing tool {tool_name} with args {tool_args}")
                output = await chosen_tool.ainvoke(tool_args, config)
                # print(f"--- Tool output: {output}")
                tool_outputs.append(
                    ToolMessage(
                        content=str(output),
                        name=tool_name,
                        tool_call_id=tool_call["id"],
                    )
                )
            except Exception as e:
                tool_outputs.append(
                    ToolMessage(
                        content=f"Error executing tool {tool_name}: {e}",
                        name=tool_name,
                        tool_call_id=tool_call["id"],
                    )
                )
        else:
            tool_outputs.append(
                ToolMessage(
                    content=f"Tool {tool_name} not found.",
                    name=tool_name,
                    tool_call_id=tool_call["id"],
                )
            )
    return {"messages": tool_outputs}


# --- 4. Define Edge Logic ---
# This function decides the next step based on the LLM's response
def should_continue(state: AgentState) -> Literal["call_tool", "end"]:
    messages = state["messages"]
    last_message = messages[-1]

    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        # If the LLM wants to call a tool, go to the tool node
        return "call_tool"
    else:
        # Otherwise, the LLM has made a final answer
        return "end"


# --- 5. Build the Graph ---
workflow = StateGraph(AgentState)

workflow.add_node("llm", call_model)
workflow.add_node("tool", call_tool)

# Define the workflow entry point
workflow.add_edge(START, "llm")

# Conditional edge from LLM: call tool or end
workflow.add_conditional_edges(
    "llm",
    should_continue,
    {"call_tool": "tool", "end": END},
)

# From tool, always go back to LLM to process tool output
workflow.add_edge("tool", "llm")

# Compile the graph
executor_graph = workflow.compile()


# --- 6. Helper for Execution ---
# Function to prepare initial state and run
async def execute_step_stream(
    step_text: str, plan_context: str, prev_step_result: str | None = None
):
    initial_messages: List[BaseMessage] = []

    # Construct a detailed prompt for the agent
    prompt_template = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You are a helpful assistant designed to execute single steps of a larger plan."
                " You have access to tools to help you achieve the step's objective."
                " You MUST use tools to gather information or perform actions when necessary."
                " When you have completed the step and found the answer or taken the action,"
                " respond with the final outcome/result in a concise manner without calling any more tools."
                " If the user asks for information you do not have, state that clearly."
                " If a step requires subjective judgement, make a reasonable, concise decision.",
            ),
            (
                "user",
                f"The overall plan context is: {plan_context}\n\n"
                f"Your current step is: {step_text}\n",
            ),
        ]
    )

    # Format the messages
    messages = await prompt_template.ainvoke(
        {}
    )  # Empty dict as variables are in f-strings above
    initial_messages.extend(messages.to_messages())

    if prev_step_result:
        initial_messages.append(
            HumanMessage(content=f"Previous step result: {prev_step_result}")
        )

    # Stream the events
    async for event in executor_graph.astream(
        {"messages": initial_messages, "outcome": None}, config={"recursion_limit": 50}
    ):
        yield event
