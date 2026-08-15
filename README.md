# SEO Blog Automation System: RAG-Powered Content Generation

An SEO content research project that compares Retrieval-Augmented Generation (RAG) against baseline LLM generation. The system retrieves evidence from a curated SEO knowledge base, generates cited blog drafts, scores output quality, and stores experiment results for comparison.

The project is designed to demonstrate that RAG can improve factual grounding and source attribution for domain-specific content generation, especially when the baseline model is asked to answer without retrieved context.

## Live Demo

**Dashboard:** https://seo-blog-automation-djhzdxtpwuzr4dlxyhwsee.streamlit.app
**Backend API docs:** https://seo-blog-backend-tjan.onrender.com/docs

> Note: the backend runs on a free-tier instance and may take 30-60 seconds to wake up if it's been idle. If the dashboard shows "Backend Offline" on first load, wait a moment and refresh.

## Core Capabilities

- Heading-aware semantic chunking for markdown knowledge-base documents
- Multi-query expansion with seven semantic query variations per keyword
- ChromaDB vector storage with deterministic lightweight embeddings
- Gemini-powered blog generation with retrieved source context
- SEO scoring across keyword density, word count, readability, structure, and keyword placement
- RAG vs baseline experiment workflow with stored metrics
- Streamlit dashboard for generation, retrieval explainability, knowledge-base inspection, and SEO audit utilities

## Project Structure

```text
SEO_BLOG_AUTOMATION/
|-- backend/
|   |-- app/
|   |   |-- api/              # FastAPI route modules
|   |   |-- core/             # configuration and path helpers
|   |   |-- db/               # database setup
|   |   |-- models/           # SQLAlchemy and response models
|   |   `-- services/         # RAG, LLM, vector store, scoring services
|   `-- knowledge_base/       # mirrored markdown corpus for backend-only deploys
|-- data/
|   |-- knowledge_base/       # primary 20-document SEO markdown corpus
|   `-- vector_store/         # local ChromaDB persistence, ignored if regenerated
|-- frontend/
|   `-- streamlit_app.py      # research dashboard
|-- scripts/
|   `-- ingest_all.py         # knowledge-base ingestion script
|-- requirements.txt
|-- runtime.txt
`-- README.md
```

## Knowledge Base

The curated corpus contains 20 SEO markdown documents covering:

- SEO fundamentals and keyword research
- Technical SEO, crawling, indexing, canonicalization, redirects, and sitemaps
- On-page SEO, SEO copywriting, content strategy, and content quality
- E-E-A-T, ranking systems, and helpful content principles
- Core Web Vitals, page speed, mobile SEO, and URL architecture
- Structured data, video SEO, local SEO, international SEO, voice search, analytics, and SEO tools

The documents cite authoritative sources such as Google Search Central, web.dev, Moz, Ahrefs, HubSpot, Schema.org, Google Search Console Help, and Google Business Profile Help. Each markdown file includes source metadata and canonical source URLs so retrieved chunks can be traced back to the material used during generation.

## RAG Pipeline

1. Markdown files are ingested from `data/knowledge_base` when available, with `backend/knowledge_base` as a fallback for backend-only deployments.
2. Documents are split by markdown H2 and H3 headings so chunks preserve semantic sections.
3. Each keyword is expanded into related search phrases before retrieval.
4. ChromaDB returns the most relevant chunks and their metadata.
5. Gemini receives the retrieved context and is instructed to cite sources inline using `[Source: Name]` notation.
6. Generated posts are scored and stored for dashboard analysis.

## SEO Scoring Formula

| Metric | Points | Target |
|---|---:|---|
| Keyword density | 25 | Natural usage, strongest around 1.0-2.0% |
| Word count | 25 | Full credit at 1,000+ words |
| Readability | 10 | Flesch Reading Ease, clamped from 0-100 |
| Content structure | 28 | H2 and H3 heading coverage |
| Keyword placement | 12 | Keyword in title and early introduction |
| Total | 100 | |

The scoring model is intentionally simple and transparent. It is useful for comparing controlled generations inside this project, not as a universal SEO ranking predictor.

## Setup

### 1. Create and activate a virtual environment

```bash
conda create -n seo_blog_env python=3.11
conda activate seo_blog_env
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure environment variables

Create a `.env` file in the project root and add:

```env
GEMINI_API_KEY=your_gemini_api_key
PAGESPEED_API_KEY=your_pagespeed_api_key

# Optional — enables AI-generated blog header images via Hugging Face.
# Not set in the live deployment; the app runs fully without it.
# HF_API_KEY=your_hugging_face_key
```

### 4. Ingest the knowledge base

```bash
python scripts/ingest_all.py
```

### 5. Run the backend

From the project root:

```bash
uvicorn backend.app.main:app --reload
```

### 6. Run the Streamlit dashboard

In a second terminal:

```bash
streamlit run frontend/streamlit_app.py
```

Open `http://localhost:8501`.

## Render Deployment Notes

For a backend deployment on Render, use the repository root as the build context when possible.

Recommended start command:

```bash
uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT
```

If Render is configured with `backend` as the root directory, keep the mirrored `backend/knowledge_base` directory included so ingestion still has access to all 20 documents.

## Research Framing

This project compares two generation modes:

- Baseline LLM: generates from the prompt without retrieved knowledge-base context.
- RAG LLM: retrieves relevant SEO chunks first and generates from that grounded context.

The strongest expected advantage of RAG is not merely a higher SEO score. It is improved factual grounding, clearer source attribution, and better traceability from generated claims back to curated source material.

## Results (19 experiments)

- **SEO score:** no statistically significant difference between RAG and baseline (avg delta approximately -0.1 pts, p = 0.62). The scoring formula used here (keyword density, structure, readability, word count) does not reward source grounding, so this result is expected rather than a shortfall.
- **Citation grounding:** RAG-generated posts cited 4-8 verified sources per post in every experiment. Baseline posts, generated without retrieval, cited zero sources in every experiment. This is the consistent, structural advantage the RAG pipeline is actually designed to produce.
- **Takeaway:** for this scoring formula, RAG and baseline are indistinguishable on SEO score alone. The real differentiator is factual traceability — RAG output can be checked against its sources; baseline output cannot. A scoring formula that accounted for citation/grounding would likely separate the two conditions more clearly.

The dataset is actively growing as more experiments are run through the pipeline.

## Important Notes

- Generated content should be reviewed by a human before publication.
- Search guidance changes over time, so the knowledge base should be periodically refreshed.
- The ChromaDB vector store is regenerated from the markdown corpus on ingestion. The SQLite database (`data/seo_blog.db`) holds real experiment run history and generated blog output — it is not a disposable artifact and is committed to the repo so the deployed dashboard reflects actual results.
- API availability, model behavior, and rate limits can affect generation quality.

## Author & Contact

Ashmita Sharma  
Email: as.ashmitasharma93@gmail.com
Linkedin: https://linkedin.com/in/ashmitasharma93034
