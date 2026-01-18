# builtin
from datetime import datetime

# third
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_core.tools import tool


@tool
def web_search(query: str) -> str:
    """
    Search the web for general information, current events, or specific data points.
    Use this for any knowledge that is not likely to be in your internal training data.
    """
    search = DuckDuckGoSearchRun()
    return search.invoke(query)


@tool
def calculator(expression: str) -> str:
    """
    Evaluate a mathematical expression.
    Useful for budgeting, scheduling, or unit conversions.
    """
    try:
        # Security: strictly limiting eval is better,
        # but for a local tool this is acceptable for now.
        # In a real prod env, use a proper parser library.
        return str(eval(expression, {"__builtins__": None}, {}))
    except Exception as e:
        return f"Error calculating: {e}"


@tool
def get_system_time() -> str:
    """
    Returns the current system time in ISO 8601 format (YYYY-MM-DD HH:MM:SS).
    Useful for scheduling, planning, or understanding the current date and time context.
    """
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


# Registry list for easy import
available_tools = [web_search, calculator, get_system_time]
