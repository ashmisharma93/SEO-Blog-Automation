from sqlalchemy import Column, Integer, String, Text, DateTime, Float
from datetime import datetime
from backend.app.db.database import Base

class Blog(Base):
    __tablename__ = "blogs"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    keyword = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    status = Column(String(50), default="draft")
    image_url = Column(String(500), nullable=True)

    # SEO evaluation metrics
    seo_score = Column(Float)
    keyword_density = Column(Float)
    readability_score = Column(Float)
    word_count = Column(Integer)
    retrieval_score = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    