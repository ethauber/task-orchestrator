import json

from langchain_ollama import ChatOllama

from backend import settings
from backend.llm.tools import normalize_duration


base_chat_llm = ChatOllama(
    model=settings.model_name or '',
    base_url=settings.ollama_base_url,
    temperature=settings.temperature
)
math_llm = base_chat_llm.bind_tools([normalize_duration])


def load_prompts(filename):
    with open(f'backend/llm/prompts/{filename}', 'r') as f:
        return json.load(f)
