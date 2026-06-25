import chromadb
from sentence_transformers import SentenceTransformer
from backend.app.core.paths import get_vector_store_path

# Embedding Model Management
# CURRENT_MODEL_NAME = "all-mpnet-base-v2"
CURRENT_MODEL_NAME = "all-MiniLM-L6-v2"
embedding_model = SentenceTransformer(CURRENT_MODEL_NAME)


def set_embedding_model(model_name: str):
    """
    Dynamically switch embedding model.
    Useful for retrieval experiments.
    """

    global embedding_model
    global CURRENT_MODEL_NAME

    print(f"\nSwitching embedding model to {model_name}\n")

    # embedding_model = SentenceTransformer(model_name)
    embedding_model = None
    CURRENT_MODEL_NAME = model_name

def get_embedding_model():
    global embedding_model

    if embedding_model is None:
        embedding_model = SentenceTransformer(CURRENT_MODEL_NAME)

    return embedding_model  


def get_current_embedding_model():
    """
    Returns the currently active embedding model name.
    """

    return CURRENT_MODEL_NAME


def generate_embedding(text: str):
    """
    Generate embedding vector for given text.
    """

    # return embedding_model.encode(text).tolist()
    model = get_embedding_model()
    return model.encode(text).tolist()

CHROMA_PATH = str(get_vector_store_path())

print(f"ChromaDB path: {CHROMA_PATH}")
chroma_client = chromadb.PersistentClient(path=CHROMA_PATH)

collection = chroma_client.get_or_create_collection(
    name="seo_knowledge_base"
)
