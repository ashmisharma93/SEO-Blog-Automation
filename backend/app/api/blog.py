from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from backend.app.db.database import get_db
from backend.app.models.blog_schema import BlogCreate, BlogResponse
from backend.app.models.blog import Blog
from backend.app.services.blog_service import create_blog

router = APIRouter(prefix="/blogs", tags=["Blogs"])


# Create Blog
@router.post("/", response_model=BlogResponse)
def create_blog_endpoint(blog: BlogCreate, db: Session = Depends(get_db)):
    return create_blog(db, blog.title, blog.keyword)


# Get All Blogs (metadata list)
@router.get("/", response_model=List[BlogResponse])
def get_all_blogs(db: Session = Depends(get_db)):
    blogs = db.query(Blog).all()
    return blogs


# Get Blog By ID (full content)
@router.get("/{blog_id}", response_model=BlogResponse)
def get_blog_by_id(blog_id: int, db: Session = Depends(get_db)):
    blog = db.query(Blog).filter(Blog.id == blog_id).first()

    if not blog:
        raise HTTPException(status_code=404, detail="Blog not found")

    return blog