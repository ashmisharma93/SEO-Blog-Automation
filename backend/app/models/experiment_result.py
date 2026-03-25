from sqlalchemy import Column, Integer, String, Float, DateTime
from datetime import datetime
from backend.app.db.database import Base


class ExperimentResult(Base):
    __tablename__ = "experiment_results"

    id = Column(Integer, primary_key=True, index=True)
    keyword = Column(String(255), nullable=False)
    chunking_strategy = Column(String(50), default="heading")  # heading | fixed
    embedding_model = Column(String(100), default="all-MiniLM-L6-v2")

    # Baseline metrics
    baseline_seo_score = Column(Float)
    baseline_keyword_density = Column(Float)
    baseline_readability = Column(Float)
    baseline_word_count = Column(Integer)

    # RAG metrics
    rag_seo_score = Column(Float)
    rag_keyword_density = Column(Float)
    rag_readability = Column(Float)
    rag_word_count = Column(Integer)

    # Retrieval quality
    avg_similarity_score = Column(Float)
    chunks_retrieved = Column(Integer)

    # Improvement deltas (computed on save)
    seo_improvement = Column(Float)        # rag_seo - baseline_seo
    readability_improvement = Column(Float)

    created_at = Column(DateTime, default=datetime.utcnow)