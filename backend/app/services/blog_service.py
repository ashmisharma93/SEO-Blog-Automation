from sqlalchemy.orm import Session
from backend.app.models.blog import Blog
from backend.app.services.rag_service import retrieve_relevant_chunks
from backend.app.services.llm_service import generate_seo_blog, generate_blog_image_url
from backend.app.services.seo_analyzer import analyze_seo


def create_blog(db: Session, title: str, keyword: str):
    """
    Orchestrates the full pipeline:

    1. Retrieve context from RAG
    2. Generate blog via LLM
    3. Generate header image via AI
    4. Analyze SEO quality
    5. Store blog + evaluation metrics in database
    """

    # 1️⃣ Retrieve context from RAG
    retrieved = retrieve_relevant_chunks(keyword, top_k=5)

    # Extract chunks, similarity scores, and source metadata
    context_chunks = [item["text"] for item in retrieved]
    similarity_scores = [item["similarity_score"] for item in retrieved]
    source_metadata = [
        {"title": item.get("title", "SEO Knowledge Base"), "source": item.get("source", "unknown")}
        for item in retrieved
    ]

    # Compute average retrieval similarity
    avg_retrieval_score = (
        sum(similarity_scores) / len(similarity_scores)
        if similarity_scores else None
    )

    print("\n---------------------------")
    print(f"Query: {keyword}")
    print(f"Retrieved similarity scores: {similarity_scores}")
    print(f"Average retrieval score: {avg_retrieval_score}")
    print("---------------------------\n")

    # 2️⃣ Generate blog via LLM
    generated_content = generate_seo_blog(
        keyword=keyword,
        context_chunks=context_chunks,
        source_metadata=source_metadata
    )

    # 3️⃣ Generate header image (free, no API key needed)
    image_url = generate_blog_image_url(keyword)
    print(f"Generated image URL for '{keyword}': {image_url}")

    # 4️⃣ Analyze SEO quality
    metrics = analyze_seo(generated_content, keyword)

    # 5️⃣ Save blog to database
    blog = Blog(
        title=title,
        keyword=keyword,
        content=generated_content,
        status="generated",
        image_url=image_url,

        # SEO evaluation metrics
        seo_score=metrics["seo_score"],
        keyword_density=metrics["keyword_density"],
        readability_score=metrics["readability_score"],
        word_count=metrics["word_count"],

        # Retrieval evaluation metric (for research analysis)
        retrieval_score=avg_retrieval_score
    )

    db.add(blog)
    db.commit()
    db.refresh(blog)

    return blog


def get_all_blogs(db: Session):
    """
    Retrieve all generated blogs.
    """
    return db.query(Blog).all()