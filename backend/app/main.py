from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.app.core.config import settings
from backend.app.api.health import router as health_router
from backend.app.db.database import engine, Base
from backend.app.api.blog import router as blog_router
from backend.app import models
from backend.app.api.rag import router as rag_router

# Import all models so Base.metadata knows about them
from backend.app.models import blog, knowledge_source, document_chunk
from backend.app.models.experiment_result import ExperimentResult  # NEW


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.PROJECT_NAME,
        version="1.0.0",
    )

    # Allow frontend (React dev server) to call the API
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:5173", "http://localhost:3000", "*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Create all tables (including experiment_results)
    Base.metadata.create_all(bind=engine)

    app.include_router(health_router)
    app.include_router(blog_router)
    app.include_router(rag_router)

    return app


app = create_app()