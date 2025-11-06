from langchain_ollama import ChatOllama

from backend import settings


base_chat_llm = ChatOllama(
    model=settings.model_name or '',
    base_url=settings.ollama_base_url,
    temperature=settings.temperature
)