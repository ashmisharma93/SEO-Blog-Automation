import os

EMBEDDING_MODE = os.getenv("EMBEDDING_MODE", "minilm")

if EMBEDDING_MODE == "hash":
    from backend.app.services.vector_store_hash import *
else:
    from backend.app.services.vector_store_minilm import *