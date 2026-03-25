from sqlalchemy.orm import Session
from sqlalchemy import func
from scipy import stats as scipy_stats

from backend.app.services.rag_service import retrieve_relevant_chunks
from backend.app.services.llm_service import generate_seo_blog, generate_seo_blog_without_rag
from backend.app.services.seo_analyzer import analyze_seo
from backend.app.services.vector_store import get_current_embedding_model
from backend.app.models.experiment_result import ExperimentResult


def run_experiment(keyword: str, db: Session, chunking_strategy: str = "heading"):
    """
    Runs comparison experiment between:
    1. Baseline LLM (no RAG)
    2. RAG-based blog generation

    Persists results to DB and returns metrics.
    """
    try:
        baseline_blog = generate_seo_blog_without_rag(keyword)
    except Exception as e:
        raise Exception(f"Baselinen generation failed: {str(e)}")
    
    try:
        retrieved = retrieve_relevant_chunks(keyword, top_k=5)
        context_chunks = [item["text"] for item in retrieved]
        similarity_scores = [item["similarity_score"] for item in retrieved]
        rag_blog = generate_seo_blog(keyword=keyword, context_chunks=context_chunks)
    except Exception as e:
        raise Exception(f"RAG generation failed: {str(e)}")
    
    # ── Baseline ──────────────────────────────────────────────
    baseline_blog = generate_seo_blog_without_rag(keyword)
    baseline_metrics = analyze_seo(baseline_blog, keyword)

    # ── RAG ───────────────────────────────────────────────────
    retrieved = retrieve_relevant_chunks(keyword, top_k=5)
    context_chunks = [item["text"] for item in retrieved]
    similarity_scores = [item["similarity_score"] for item in retrieved]

    avg_similarity = (
        sum(similarity_scores) / len(similarity_scores) if similarity_scores else None
    )

    rag_blog = generate_seo_blog(keyword=keyword, context_chunks=context_chunks)
    rag_metrics = analyze_seo(rag_blog, keyword)

    # ── Compute Deltas ────────────────────────────────────────
    seo_improvement = rag_metrics["seo_score"] - baseline_metrics["seo_score"]
    readability_improvement = (
        rag_metrics["readability_score"] - baseline_metrics["readability_score"]
    )
    citation_improvement = (
        rag_metrics.get("citation_count", 0) - baseline_metrics.get("citation_count", 0)
    )

    # ── Persist to DB ─────────────────────────────────────────
    record = ExperimentResult(
        keyword=keyword,
        chunking_strategy=chunking_strategy,
        embedding_model=get_current_embedding_model(),

        baseline_seo_score=baseline_metrics["seo_score"],
        baseline_keyword_density=baseline_metrics["keyword_density"],
        baseline_readability=baseline_metrics["readability_score"],
        baseline_word_count=baseline_metrics["word_count"],

        rag_seo_score=rag_metrics["seo_score"],
        rag_keyword_density=rag_metrics["keyword_density"],
        rag_readability=rag_metrics["readability_score"],
        rag_word_count=rag_metrics["word_count"],

        avg_similarity_score=avg_similarity,
        chunks_retrieved=len(context_chunks),
        seo_improvement=seo_improvement,
        readability_improvement=readability_improvement,
    )

    db.add(record)
    db.commit()
    db.refresh(record)

    return {
        "id": record.id,
        "keyword": keyword,
        "chunking_strategy": chunking_strategy,
        "baseline": {
            "seo_score":        baseline_metrics["seo_score"],
            "keyword_density":  baseline_metrics["keyword_density"],
            "readability_score":baseline_metrics["readability_score"],
            "word_count":       baseline_metrics["word_count"],
            "citation_count":   baseline_metrics.get("citation_count", 0),
        },
        "rag_system": {
            "seo_score":        rag_metrics["seo_score"],
            "keyword_density":  rag_metrics["keyword_density"],
            "readability_score":rag_metrics["readability_score"],
            "word_count":       rag_metrics["word_count"],
            "citation_count":   rag_metrics.get("citation_count", 0),
        },
        "retrieval_quality": {
            "avg_similarity_score": avg_similarity,
            "chunks_retrieved": len(context_chunks),
        },
        "improvements": {
            "seo_score_delta":      round(seo_improvement, 2),
            "readability_delta":    round(readability_improvement, 2),
            "citation_improvement": round(citation_improvement, 2),
        },
        "citations": {
            "baseline_citations": baseline_metrics.get("citation_count", 0),
            "rag_citations":      rag_metrics.get("citation_count", 0),
        },
    }

def get_experiment_summary(db: Session):
    results = db.query(ExperimentResult).all()

    if not results:
        return {"message": "No experiments run yet.", "total_experiments": 0}

    baseline_seo = [r.baseline_seo_score for r in results]
    rag_seo      = [r.rag_seo_score for r in results]
    baseline_read = [r.baseline_readability for r in results]
    rag_read      = [r.rag_readability for r in results]
    improvements  = [r.seo_improvement for r in results]

    t_stat, p_value = scipy_stats.ttest_rel(rag_seo, baseline_seo)
    avg = lambda lst: round(sum(lst) / len(lst), 2) if lst else 0

    return {
        "total_experiments": len(results),
        "keywords_tested": list({r.keyword for r in results}),
        "averages": {
            "baseline_seo": avg(baseline_seo),
            "rag_seo": avg(rag_seo),
            "baseline_readability": avg(baseline_read),
            "rag_readability": avg(rag_read),
            "avg_seo_improvement": avg(improvements),
            "avg_similarity_score": avg(
                [r.avg_similarity_score for r in results if r.avg_similarity_score]
            ),
        },
        "statistical_significance": {
            "t_statistic": round(float(t_stat), 4),
            "p_value": round(float(p_value), 4),
            "significant_at_0.05": bool(p_value < 0.05),
            "interpretation": (
                "RAG significantly outperforms baseline (p < 0.05)"
                if p_value < 0.05
                else "No significant difference detected yet — run more experiments"
            ),
        },
        "per_experiment": [
            {
                "id": r.id,
                "keyword": r.keyword,
                "baseline_seo": r.baseline_seo_score,
                "rag_seo": r.rag_seo_score,
                "seo_improvement": r.seo_improvement,
                "avg_similarity": r.avg_similarity_score,
                "created_at": r.created_at.isoformat(),
            }
            for r in results
        ],
    }