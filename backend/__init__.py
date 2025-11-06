import os

from dotenv import load_dotenv

from backend.config import Settings

settings = Settings()

load_dotenv()

# lazy-init ollama client
try:
    from ollama import Client
    ollama_client = Client(host=settings.ollama_base_url)
except Exception as ollama_init_error:
    print(
        "Warning: could not initialize ollama client at"
        f" {settings.ollama_base_url}\n{ollama_init_error}"
    )
    ollama_client = None
