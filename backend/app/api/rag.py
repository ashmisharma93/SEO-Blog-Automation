from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from backend.app.db.database import get_db
from backend.app.services.rag_service import ingest_knowledge_source, retrieve_relevant_chunks
from backend.app.services.experiment_service import run_experiment, get_experiment_summary
from backend.app.services.vector_store import chroma_client, get_current_embedding_model

router = APIRouter(prefix="/rag", tags=["RAG"])


# Request Schemas 

class IngestRequest(BaseModel):
    title: str
    content: str


class RetrieveRequest(BaseModel):
    query: str
    top_k: int = 3


# Ingest 

@router.post("/ingest")
def ingest(request: IngestRequest, db: Session = Depends(get_db)):
    return ingest_knowledge_source(db, request.title, request.content)


# Retrieve 

@router.post("/retrieve")
def retrieve(request: RetrieveRequest):
    return retrieve_relevant_chunks(request.query, request.top_k)


@router.get("/knowledge-base/stats")
def knowledge_base_stats():
    collection = chroma_client.get_or_create_collection(name="seo_knowledge_base")
    data = collection.get(include=["metadatas", "documents"])
    metadatas = data.get("metadatas", []) or []
    documents = data.get("documents", []) or []

    doc_stats = {}
    for meta, document in zip(metadatas, documents):
        meta = meta or {}
        title = meta.get("title", "Unknown")
        if title not in doc_stats:
            doc_stats[title] = {
                "title": title,
                "category": meta.get("category", "Unknown"),
                "source": meta.get("source", "Unknown"),
                "source_url": meta.get("source_url", ""),
                "chunks": 0,
                "total_chars": 0,
                "previews": [],
            }
        doc_stats[title]["chunks"] += 1
        doc_stats[title]["total_chars"] += len(document or "")
        if len(doc_stats[title]["previews"]) < 2:
            doc_stats[title]["previews"].append((document or "")[:200])

    categories = sorted({
        (meta or {}).get("category", "Unknown")
        for meta in metadatas
    })

    return {
        "total_chunks": collection.count(),
        "knowledge_files": len(doc_stats),
        "categories": categories,
        "embedding_model": get_current_embedding_model(),
        "documents": sorted(doc_stats.values(), key=lambda item: item["chunks"], reverse=True),
    }


# Run Experiment 

@router.post("/experiments/run")
def run_rag_experiment(
    keyword: str = Query(..., description="SEO keyword to test"),
    chunking_strategy: str = Query("heading", description="heading | fixed"),
    db: Session = Depends(get_db),
):
    """
    Runs RAG vs Baseline experiment and saves results to DB.
    """
    results = run_experiment(keyword, db, chunking_strategy)
    return {
        "message": "Experiment completed successfully",
        "results": results,
    }


# Experiment Summary (Aggregated Stats + T-Test) 

@router.get("/experiments/summary")
def experiment_summary(db: Session = Depends(get_db)):
    """
    Returns aggregated stats + statistical significance test
    across all saved experiments.
    """
    return get_experiment_summary(db)


# All Experiment Records 

@router.get("/experiments/all")
def get_all_experiments(db: Session = Depends(get_db)):
    """
    Returns all individual experiment records for the dashboard.
    """
    from backend.app.models.experiment_result import ExperimentResult
    results = db.query(ExperimentResult).order_by(ExperimentResult.created_at.desc()).all()
    return [
        {
            "id": r.id,
            "keyword": r.keyword,
            "chunking_strategy": r.chunking_strategy,
            "embedding_model": r.embedding_model,
            "baseline_seo": r.baseline_seo_score,
            "rag_seo": r.rag_seo_score,
            "baseline_readability": r.baseline_readability,
            "rag_readability": r.rag_readability,
            "seo_improvement": r.seo_improvement,
            "avg_similarity_score": r.avg_similarity_score,
            "chunks_retrieved": r.chunks_retrieved,
            "created_at": r.created_at.isoformat(),
        }
        for r in results
    ]
