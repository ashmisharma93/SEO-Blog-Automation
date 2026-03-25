from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from backend.app.db.database import Base

class DocumentChunk(Base):
    __tablename__ = "document_chunks"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text, nullable=False)

    knowledge_source_id = Column(
        Integer,
        ForeignKey("knowledge_sources.id"),
        nullable = False
    )

    source = relationship("KnowledgeSource", backref="chunks")

