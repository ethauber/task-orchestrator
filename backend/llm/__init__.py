import json
import os
from langchain_ollama import ChatOllama

from backend import settings
from backend.llm.tools import normalize_duration


base_chat_llm = ChatOllama(
    model=settings.model_name or "",
    base_url=settings.ollama_base_url,
    temperature=settings.temperature,
)
math_llm = base_chat_llm.bind_tools([normalize_duration])


def load_prompts(filename):
    # Construct absolute path to the prompts directory
    # relative to THIS file (__init__.py)
    current_dir = os.path.dirname(os.path.abspath(__file__))
    prompts_path = os.path.join(current_dir, "prompts", filename)

    with open(prompts_path, "r") as f:
        return json.load(f)
