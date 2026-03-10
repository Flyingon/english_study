import os
from dotenv import load_dotenv
from pathlib import Path

# Load .env relative to this file
env_path = Path(__file__).resolve().parent / '.env'
load_dotenv(dotenv_path=env_path)

class Settings:
    # Project Settings
    PROJECT_NAME: str = "English Memory Agent"
    VERSION: str = "0.1.0"
    
    # Chroma Settings
    # Use absolute path or relative to this file
    CHROMA_PERSIST_DIRECTORY: str = os.getenv("CHROMA_PERSIST_DIRECTORY", os.path.join(os.path.dirname(__file__), "chroma_db"))
    
    # LLM Settings (Default to ZhipuAI / GLM-4)
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_BASE_URL: str = os.getenv("OPENAI_BASE_URL", "https://open.bigmodel.cn/api/paas/v4/")
    LLM_MODEL: str = os.getenv("LLM_MODEL", "glm-4-flash")
    
    # Embedding Settings
    # using all-MiniLM-L6-v2 locally by default in Chroma
    
settings = Settings()
