from langchain_core.tools import tool


@tool
def normalize_duration(minutes: int) -> int:
    """
    Rounds a task duration to the nearest 15-minute increment.
    Returns 15 if the rounded value is less than 15.
    """
    q = int(round(minutes / 15.0)) * 15
    return minutes if q < 15 else q
