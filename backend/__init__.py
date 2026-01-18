import os
from dotenv import load_dotenv

# Load .env BEFORE instantiating settings so environment variables are present
# Use absolute path to ensure it's found regardless of CWD
current_dir = os.path.dirname(os.path.abspath(__file__))
env_path = os.path.join(current_dir, ".env")
load_dotenv(env_path)

from backend.config import Settings

settings = Settings()

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
