import os
import sys
from dotenv import load_dotenv

# Load environment variables explicitly
current_dir = os.path.dirname(os.path.abspath(__file__))
dotenv_path = os.path.join(current_dir, "backend", ".env")
load_dotenv(dotenv_path)

# Correct import: settings is instantiated in backend/__init__.py
from backend import settings
from backend.llm import base_chat_llm

if __name__ == "__main__":
    print(f"Loading env from: {dotenv_path}")
    print(f"Env file exists: {os.path.exists(dotenv_path)}")
    print(f"Model Name from settings: '{settings.model_name}'")
    print(f"Ollama Base URL from settings: '{settings.ollama_base_url}'")
    print(f"Base LLM Model: '{base_chat_llm.model}'")

    if not settings.model_name:
        print("ERROR: model_name is empty!")
        sys.exit(1)
    else:
        print("SUCCESS: Configuration loaded correctly.")
