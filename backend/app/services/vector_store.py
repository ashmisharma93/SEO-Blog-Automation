import os
import chromadb
from sentence_transformers import SentenceTransformer

# Embedding Model Management
CURRENT_MODEL_NAME = "all-mpnet-base-v2"
embedding_model = SentenceTransformer(CURRENT_MODEL_NAME)


def set_embedding_model(model_name: str):
    """
    Dynamically switch embedding model.
    Useful for retrieval experiments.
    """

    global embedding_model
    global CURRENT_MODEL_NAME

    print(f"\nSwitching embedding model → {model_name}\n")

    embedding_model = SentenceTransformer(model_name)
    CURRENT_MODEL_NAME = model_name


def get_current_embedding_model():
    """
    Returns the currently active embedding model name.
    """

    return CURRENT_MODEL_NAME


def generate_embedding(text: str):
    """
    Generate embedding vector for given text.
    """

    return embedding_model.encode(text).tolist()

_THIS_FILE = os.path.abspath(__file__)  # backend/app/services/vector_store.py
_BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.dirname(_THIS_FILE)))  # backend/
_ROOT_DIR = os.path.dirname(_BACKEND_DIR)  # project root

# Try new location first, fall back to old
_NEW_PATH = os.path.join(_ROOT_DIR, "data", "vector_store")
_OLD_PATH = os.path.join(_ROOT_DIR, "chroma_db")

if os.path.isdir(_NEW_PATH):
    CHROMA_PATH = _NEW_PATH
elif os.path.isdir(_OLD_PATH):
    CHROMA_PATH = _OLD_PATH
else:
    # Default to new location (will be created on first ingest)
    CHROMA_PATH = _NEW_PATH

print(f"ChromaDB path: {CHROMA_PATH}")
chroma_client = chromadb.PersistentClient(path=CHROMA_PATH)

collection = chroma_client.get_or_create_collection(
    name="seo_knowledge_base"
)