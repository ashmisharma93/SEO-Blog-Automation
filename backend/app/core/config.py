from dotenv import load_dotenv
import os
from backend.app.core.paths import get_database_path

load_dotenv()

class Settings:
    PROJECT_NAME: str = "SEO Blog Automation System"
    ENV: str = os.getenv("ENV", "development")

    @property
    def DATABASE_URL(self):
        env_url = os.getenv("DATABASE_URL")
        if env_url:
            return env_url
        return f"sqlite:///{get_database_path()}"

    # LLM keys
    GEMINI_API_KEY: str | None = os.getenv("GEMINI_API_KEY")

    # Image generation
    HF_API_KEY: str | None = os.getenv("HF_API_KEY")

    class Config:
        env_file = ".env"

settings = Settings()

if not settings.GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY is not set in environment variables.")
