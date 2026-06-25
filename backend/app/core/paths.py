from pathlib import Path


BACKEND_DIR = Path(__file__).resolve().parents[2]
PROJECT_ROOT = BACKEND_DIR.parent


def first_existing_path(*candidates: Path) -> Path:
    for path in candidates:
        if path.exists():
            return path
    return candidates[0]


def get_database_path() -> Path:
    return first_existing_path(
        PROJECT_ROOT / "data" / "seo_blog.db",
        BACKEND_DIR / "seo_blog.db",
        PROJECT_ROOT / "seo_blog.db",
    )


def get_knowledge_base_path() -> Path:
    return first_existing_path(
        PROJECT_ROOT / "data" / "knowledge_base",
        BACKEND_DIR / "knowledge_base",
    )


def get_vector_store_path() -> Path:
    return first_existing_path(
        PROJECT_ROOT / "data" / "vector_store",
        BACKEND_DIR / "data" / "vector_store",
        PROJECT_ROOT / "chroma_db",
    )
