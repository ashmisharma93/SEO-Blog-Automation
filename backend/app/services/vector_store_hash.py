import chromadb
import hashlib
import math
import re
from backend.app.core.paths import get_vector_store_path

CURRENT_MODEL_NAME = "hashing-embedding-384"
EMBEDDING_DIMENSIONS = 384


def set_embedding_model(model_name: str):
    """
    Keep compatibility with experiment code that records an embedding model name.
    """

    global CURRENT_MODEL_NAME

    print(f"\nSwitching embedding model to {model_name}\n")
    CURRENT_MODEL_NAME = model_name


def _tokenize(text: str):
    return re.findall(r"[a-z0-9]+", text.lower())


def get_current_embedding_model():
    """
    Returns the currently active embedding model name.
    """

    return CURRENT_MODEL_NAME


def generate_embedding(text: str):
    """
    Generate a deterministic lightweight embedding vector for ChromaDB.

    This avoids loading PyTorch on small hosted instances while keeping retrieval
    reproducible across local and Render deployments.
    """

    vector = [0.0] * EMBEDDING_DIMENSIONS
    tokens = _tokenize(text)

    for token in tokens:
        digest = hashlib.blake2b(token.encode("utf-8"), digest_size=8).digest()
        value = int.from_bytes(digest, "big")
        index = value % EMBEDDING_DIMENSIONS
        sign = 1.0 if ((value >> 8) & 1) else -1.0
        vector[index] += sign

    norm = math.sqrt(sum(value * value for value in vector))
    if norm == 0:
        return vector
    return [value / norm for value in vector]

CHROMA_PATH = str(get_vector_store_path())

print(f"ChromaDB path: {CHROMA_PATH}")
chroma_client = chromadb.PersistentClient(path=CHROMA_PATH)

collection = chroma_client.get_or_create_collection(
    name="seo_knowledge_base"
)