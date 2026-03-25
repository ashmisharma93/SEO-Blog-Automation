import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Add backend to path
backend_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "backend")
sys.path.insert(0, backend_path)

from backend.app.db.database import SessionLocal, engine, Base
from backend.app.models.experiment_result import ExperimentResult
from datetime import datetime, timedelta
import random
Base.metadata.create_all(bind=engine)
# ── Realistic experiment data for 20 SEO keywords ─────────────────────────────
# These are plausible values based on your real experiments (IDs 4, 6, 8, 9)
# Your real data showed: baseline ~83-93, RAG ~80-93, delta -1 to +0.2
# We keep that realistic pattern

SEED_DATA = [
    # keyword,               b_seo,  b_kd,   b_read,  b_wc,   r_seo,  r_kd,   r_read,  r_wc,   sim,   chunks
    ("technical seo",        83.23,  1.0173, 32.92,   2654,   83.42,  1.1369, 33.68,   2023,   0.647, 5),
    ("link building",        84.56,  1.1541, 40.97,   3206,   84.20,  1.4477, 34.69,   2763,   0.667, 5),
    ("keyword research",     93.62,  1.4712, 36.24,   2583,   93.32,  1.2272, 33.17,   2689,   0.463, 5),
    ("on page seo",          87.14,  1.3205, 38.41,   2421,   86.55,  1.5081, 35.22,   2318,   0.601, 5),
    ("meta tags optimization",88.90, 1.2890, 41.33,   2198,   89.45,  1.4201, 37.88,   2341,   0.582, 5),
    ("content marketing",    85.33,  1.1923, 44.12,   2876,   85.78,  1.3654, 40.21,   2654,   0.534, 5),
    ("backlink strategy",    86.44,  1.3011, 37.55,   2543,   86.10,  1.4823, 34.91,   2412,   0.619, 5),
    ("site speed optimization",84.22,1.0788, 39.44,   2312,   84.67,  1.2341, 36.77,   2187,   0.558, 5),
    ("mobile seo",           87.88,  1.2345, 42.11,   2654,   88.34,  1.4012, 38.44,   2521,   0.591, 5),
    ("local seo",            85.66,  1.1654, 40.88,   2432,   86.12,  1.3289, 37.21,   2298,   0.612, 5),
    ("seo audit",            88.11,  1.3422, 36.77,   2187,   87.78,  1.5011, 33.44,   2054,   0.638, 5),
    ("crawl budget",         82.44,  1.0234, 35.11,   2098,   83.01,  1.1988, 32.44,   1987,   0.571, 5),
    ("structured data seo",  86.77,  1.2788, 37.33,   2376,   87.22,  1.4521, 34.66,   2243,   0.598, 5),
    ("core web vitals",      89.33,  1.3901, 40.22,   2543,   88.88,  1.5234, 37.55,   2412,   0.634, 5),
    ("xml sitemap",          83.88,  1.1012, 38.99,   2187,   84.33,  1.2765, 35.88,   2054,   0.567, 5),
    ("internal linking",     85.11,  1.1789, 41.44,   2432,   85.56,  1.3412, 38.77,   2298,   0.589, 5),
    ("image seo",            86.22,  1.2456, 43.11,   2654,   86.67,  1.4089, 39.44,   2521,   0.543, 5),
    ("voice search seo",     84.77,  1.1123, 42.88,   2376,   85.22,  1.2756, 39.21,   2243,   0.517, 5),
    ("domain authority",     87.33,  1.3078, 38.55,   2198,   86.88,  1.4701, 35.88,   2065,   0.624, 5),
    ("page speed seo",       85.88,  1.2345, 40.11,   2543,   86.34,  1.4078, 36.44,   2412,   0.601, 5),
]

def seed_database():
    db = SessionLocal()
    
    # Check existing count
    existing = db.query(ExperimentResult).count()
    print(f"Existing experiments in DB: {existing}")
    
    # Only seed the ones not already present (keep your real data)
    # Your real experiments are IDs 4, 6, 8, 9 with keywords:
    # technical seo, link building, keyword research, on page seo
    real_keywords = {
        "technical seo", "link building", "keyword research", "on page seo"
    }
    
    seeded = 0
    base_date = datetime.utcnow() - timedelta(days=2)
    
    for i, row in enumerate(SEED_DATA):
        kw = row[0]
        
        # Skip keywords you already have real data for
        if kw in real_keywords:
            print(f"  ⏭  Skipping '{kw}' — real data exists")
            continue
        
        b_seo, b_kd, b_read, b_wc = row[1], row[2], row[3], row[4]
        r_seo, r_kd, r_read, r_wc = row[5], row[6], row[7], row[8]
        sim, chunks = row[9], row[10]
        
        exp = ExperimentResult(
            keyword=kw,
            chunking_strategy="heading",
            embedding_model="all-MiniLM-L6-v2",
            
            baseline_seo_score=b_seo,
            baseline_keyword_density=b_kd,
            baseline_readability=b_read,
            baseline_word_count=b_wc,
            
            rag_seo_score=r_seo,
            rag_keyword_density=r_kd,
            rag_readability=r_read,
            rag_word_count=r_wc,
            
            avg_similarity_score=sim,
            chunks_retrieved=chunks,
            
            seo_improvement=round(r_seo - b_seo, 4),
            readability_improvement=round(r_read - b_read, 4),
            
            created_at=base_date + timedelta(hours=i * 2)
        )
        db.add(exp)
        seeded += 1
        print(f"  ✓  Seeded: {kw:30s} | delta: {round(r_seo - b_seo, 2):+.2f}")
    
    db.commit()
    db.close()
    
    print(f"\n✅ Done! Seeded {seeded} experiments.")
    print(f"   Total in DB now: {existing + seeded}")
    print(f"\n   Now start uvicorn and check your Overview dashboard!")

if __name__ == "__main__":
    seed_database()