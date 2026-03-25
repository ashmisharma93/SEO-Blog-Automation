import re
from sqlalchemy.orm import Session
from backend.app.models.knowledge_source import KnowledgeSource
from backend.app.models.document_chunk import DocumentChunk
from backend.app.services.vector_store import generate_embedding, chroma_client


# ── Chunking Strategies ───────────────────────────────────────────────────────

def split_by_headings(content: str):
    """
    Semantic chunking: split on markdown ## and ### headings.
    Keeps heading attached to its content block.
    """
    if content.startswith("---"):
        parts = content.split("---")
        if len(parts) > 2:
            content = "---".join(parts[2:]).strip()

    sections = re.split(r"(?=^\s*##\s|^\s*###\s)", content, flags=re.MULTILINE)
    chunks = [s.strip() for s in sections if s.strip()]

    if not chunks:
        chunks = split_by_fixed_size(content)

    return chunks


def split_by_fixed_size(content: str, chunk_size: int = 600):
    """
    Naive fixed-size chunking — used as baseline for comparison.
    """
    return [content[i:i + chunk_size] for i in range(0, len(content), chunk_size)]


def split_text(content: str, strategy: str = "heading"):
    """
    Dispatch to the correct chunking strategy.
    strategy: "heading" | "fixed"
    """
    if strategy == "fixed":
        return split_by_fixed_size(content)
    return split_by_headings(content)


# ── Ingest Knowledge Source ───────────────────────────────────────────────────

def ingest_knowledge_source(
    db: Session,
    title: str,
    content: str,
    category: str = "general",
    domain: str = "seo",
    source: str = "unknown",
    chunking_strategy: str = "heading",   # NEW: strategy param
):
    # Always fetch the live collection — avoids stale reference after delete/recreate
    collection = chroma_client.get_or_create_collection(name="seo_knowledge_base")
    """
    1. Save KnowledgeSource in SQL
    2. Chunk content (strategy: heading | fixed)
    3. Store chunks in SQL
    4. Generate embeddings
    5. Store embeddings in ChromaDB with metadata
    """

    source_record = KnowledgeSource(title=title, content=content)
    db.add(source_record)
    db.commit()
    db.refresh(source_record)

    chunks = split_text(content, strategy=chunking_strategy)

    for chunk in chunks:
        db_chunk = DocumentChunk(
            content=chunk,
            knowledge_source_id=source_record.id,
        )
        db.add(db_chunk)
        db.commit()
        db.refresh(db_chunk)

        embedding = generate_embedding(chunk)

        try:
            collection.add(
                documents=[chunk],
                embeddings=[embedding],
                ids=[str(db_chunk.id)],
                metadatas=[{
                    "source_id": source_record.id,
                    "title": title,
                    "category": category,
                    "domain": domain,
                    "source": source,
                    "chunking_strategy": chunking_strategy,   # store for analysis
                }],
            )
        except Exception:
            collection.delete(ids=[str(db_chunk.id)])
            collection.add(
                documents=[chunk],
                embeddings=[embedding],
                ids=[str(db_chunk.id)],
                metadatas=[{
                    "source_id": source_record.id,
                    "title": title,
                    "category": category,
                    "domain": domain,
                    "source": source,
                    "chunking_strategy": chunking_strategy,
                }],
            )

    return {
        "message": "Knowledge source ingested successfully",
        "chunks_created": len(chunks),
        "chunking_strategy": chunking_strategy,
    }


# ── Query Expansion ───────────────────────────────────────────────────────────

def expand_query(query: str):
    """
    Expand query with related SEO search phrases
    to improve semantic retrieval coverage.
    """
    base = query.lower().strip()
    expansions = [
        base,
        f"{base} seo",
        f"{base} guide",
        f"{base} optimization",
        f"{base} best practices",
        f"{base} techniques",
        f"what is {base}",
    ]
    return list(set(expansions))


# ── Topic Detection ───────────────────────────────────────────────────────────

def detect_topic(query: str):
    query = query.lower()
    if any(w in query for w in ["crawl", "index", "robots", "sitemap", "technical"]):
        return "technical_seo"
    if any(w in query for w in ["keyword", "search volume", "keyword research"]):
        return "keyword_research"
    if any(w in query for w in ["meta", "title tag", "header", "on page"]):
        return "on_page_seo"
    if any(w in query for w in ["backlink", "link building"]):
        return "link_building"
    if any(w in query for w in ["content marketing", "blog strategy"]):
        return "content_marketing"
    return None


# ── Retrieve Relevant Chunks ──────────────────────────────────────────────────

def retrieve_relevant_chunks(query: str, top_k: int = 3):
    # Always fetch the live collection
    collection = chroma_client.get_or_create_collection(name="seo_knowledge_base")
    """
    Retrieve relevant chunks using:
    - Multi-query expansion
    - Domain-filtered vector search
    - Deduplication keeping best score

    Returns list of { text, similarity_score }
    """
    expanded_queries = expand_query(query)
    all_results = {}

    for q in expanded_queries:
        query_embedding = generate_embedding(q)
        topic = detect_topic(query)

        if topic:
            results = collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k,
                where={"category": topic},
            )
        else:
            results = collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k,
            )

        documents = results.get("documents", [[]])
        distances = results.get("distances", [[]])
        metadatas = results.get("metadatas", [[]])

        if not documents or not documents[0]:
            continue

        for doc, score, meta in zip(documents[0], distances[0], metadatas[0] if metadatas else [{}]*len(documents[0])):
            if score > 1.2:   # too dissimilar, skip
                continue
            if len(doc.strip()) < 50:  # too short to be useful, skip
                continue
            if doc not in all_results or score < all_results[doc]["similarity_score"]:
                all_results[doc] = {
                    "similarity_score": float(score),
                    "title": meta.get("title", "SEO Knowledge Base") if meta else "SEO Knowledge Base",
                    "source": meta.get("source", "unknown") if meta else "unknown",
                }

    retrieved_chunks = sorted(
        [
            {
                "text": doc,
                "similarity_score": info["similarity_score"],
                "title": info["title"],
                "source": info["source"],
            }
            for doc, info in all_results.items()
        ],
        key=lambda x: x["similarity_score"],
    )

    return retrieved_chunks[:top_k]