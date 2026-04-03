from dotenv import load_dotenv
from pydantic_settings import BaseSettings
import os

load_dotenv()

class Settings:
    PROJECT_NAME: str = "SEO Blog Automation System"
    ENV: str = os.getenv("ENV", "development")

    @property
    def DATABASE_URL(self):
        env_url = os.getenv("DATABASE_URL")
        if env_url:
            return env_url
        this_dir = os.path.dirname(os.path.abspath(__file__))
        backend_dir = os.path.dirname(this_dir)
        app_dir = os.path.dirname(backend_dir)
        root_dir = os.path.dirname(app_dir)

        new_db = os.path.join(root_dir, "data", "seo_blog.db")
        old_db = os.path.join(app_dir, "seo_blog.db")

        if os.path.isfile(new_db):
            return f"sqlite:///{new_db}"
        elif os.path.isfile(old_db):
            return f"sqlite:///{old_db}"
        else:
            return f"sqlite:///{new_db}"

    # LLM keys
    GEMINI_API_KEY: str | None = os.getenv("GEMINI_API_KEY")

    # Image generation
    HF_API_KEY: str | None = os.getenv("HF_API_KEY")

    class Config:
        env_file = ".env"

settings = Settings()

if not settings.GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY is not set in environment variables.")