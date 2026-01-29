from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    OLLAMA_URL: str = "http://localhost:11434"
    MODEL_NAME: str = "qwen2:7b"

settings = Settings()
