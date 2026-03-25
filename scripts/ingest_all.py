import os
import re
import sys

# ── Always run from project root ─────────────────────────────────────────────
# Adds project root to sys.path so 'backend.app.xxx' imports work correctly
_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from backend.app.db.database import SessionLocal
from backend.app.services.rag_service import ingest_knowledge_source
from backend.app.services.vector_store import chroma_client, get_current_embedding_model

# ── Knowledge Base Path (supports new and old structure) ─────────────────────
_ROOT_DIR = _PROJECT_ROOT

# New structure: data/knowledge_base/
# Old structure: backend/knowledge_base/
_NEW_KB = os.path.join(_ROOT_DIR, "data", "knowledge_base")
_OLD_KB = os.path.join(_ROOT_DIR, "backend", "knowledge_base")

if os.path.isdir(_NEW_KB):
    KNOWLEDGE_BASE_PATH = _NEW_KB
elif os.path.isdir(_OLD_KB):
    KNOWLEDGE_BASE_PATH = _OLD_KB
else:
    KNOWLEDGE_BASE_PATH = _NEW_KB  # default to new

print(f"Knowledge base path: {KNOWLEDGE_BASE_PATH}")


def extract_metadata_and_content(file_path):
    """
    Extract YAML front matter and content separately.
    """
    with open(file_path, "r", encoding="utf-8") as f:
        text = f.read()

    metadata = {}
    content = text

    if text.startswith("---"):
        parts = text.split("---")
        if len(parts) > 2:
            yaml_block = parts[1]
            content = "---".join(parts[2:]).strip()

            for line in yaml_block.split("\n"):
                if ":" in line:
                    key, value = line.split(":", 1)
                    metadata[key.strip()] = value.strip()

    return metadata, content


def ingest_all_documents():
    db = SessionLocal()

    print("Clearing existing vector collection...")

    # Delete the old collection entirely so dimension mismatch is avoided
    # This is required when switching embedding models (e.g. 384-dim to 768-dim)
    try:
        chroma_client.delete_collection("seo_knowledge_base")
        print("Old collection deleted. Recreating with new embedding dimensions...")
    except Exception as e:
        print(f"Note: {e}")

    # Recreate fresh collection
    collection = chroma_client.get_or_create_collection(name="seo_knowledge_base")
    print(f"Fresh collection created. Embedding model: {get_current_embedding_model()}")

    total_files = 0

    for root, _, files in os.walk(KNOWLEDGE_BASE_PATH):
        for file in files:
            if file.endswith(".md"):
                file_path = os.path.join(root, file)

                print(f"Ingesting: {file}")

                metadata, content = extract_metadata_and_content(file_path)

                title    = metadata.get("title",    file.replace(".md", ""))
                category = metadata.get("category", "general")
                domain   = metadata.get("domain",   "seo")
                source   = metadata.get("source",   "unknown")

                ingest_knowledge_source(
                    db,
                    title=title,
                    content=content,
                    category=category,
                    domain=domain,
                    source=source
                )

                total_files += 1

    db.close()

    print(f"\nIngestion complete. Total files processed: {total_files}")
    print(f"Total chunks in vector DB: {collection.count()}")
    print(f"Embedding model used: {get_current_embedding_model()}")


if __name__ == "__main__":
    ingest_all_documents()