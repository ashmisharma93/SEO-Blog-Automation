from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class BlogCreate(BaseModel):
    title: str
    keyword: str


class BlogResponse(BaseModel):
    id: int
    title: str
    keyword: str
    status: str
    content: str

    seo_score: Optional[float] = None
    keyword_density: Optional[float] = None
    readability_score: Optional[float] = None
    word_count: Optional[int] = None
    image_url: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True