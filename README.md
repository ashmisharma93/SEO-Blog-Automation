# ⚡ SEO Blog Automation System — RAG-Powered Content Generation

An intelligent SEO content automation system that retrieves knowledge from a structured knowledge base,
generates factually grounded blogs using Retrieval-Augmented Generation (RAG), and compares them
against baseline LLM generation through statistical evaluation.

This system uses a novel RAG architecture combining:
- ✔ Heading-Aware Semantic Chunking for knowledge base construction
- ✔ Multi-Query Expansion (7 semantic variations per keyword)
- ✔ ChromaDB Vector Store with SentenceTransformer embeddings
- ✔ Google Gemini 2.5 Flash for blog generation
- ✔ Five-Metric SEO Scoring Formula (100 pts)
- ✔ Paired T-Test Statistical Validation
- ✔ 7-Page Interactive Streamlit Research Dashboard

---

## 🚀 Features

### 🧠 RAG Pipeline with 3 Novel Contributions
- **Heading-Aware Chunking** — splits documents at H2/H3 boundaries instead of fixed character windows
- **Multi-Query Expansion** — each keyword expanded into 7 semantic variations before retrieval
- **Empirical Evaluation Framework** — five-metric scoring with Cohen's d, confidence intervals, and t-test

### 📊 Research Dashboard (7 Pages)
- Overview with RAG vs Baseline charts, citation advantage visualization, and t-test significance banner
- Experiment Lab for running live RAG vs Baseline comparisons
- Blog Generator with contextual section visuals and clickable source citations
- All Records with CSV export for thesis analysis
- RAG Explainability Panel showing query expansions and retrieved chunks
- Knowledge Base Explorer with chunk distribution charts
- SEO Site Audit powered by SEOptimer API

### 📈 Statistical Validation
- Paired t-test across 36 experiments
- Cohen's d effect size reporting
- 95% Confidence Intervals
- RAG Win Rate: 94.4% (34/36 experiments)
- p-value ≈ 0.0 — statistically significant

### 🔗 Factual Grounding (Citation Advantage)
- RAG generates 4–8 verified source citations per blog
- Baseline LLM generates 0 citations
- 100% improvement in factual grounding

---

## 📂 Project Structure

```
SEO_BLOG_AUTOMATION/
│
├── backend/
│   └── app/
│       ├── api/              # health.py, blog.py, rag.py
│       ├── core/             # config.py
│       ├── db/               # database.py
│       ├── models/           # blog.py, experiment_result.py, ...
│       └── services/         # blog_service.py, experiment_service.py,
│                             # llm_service.py, rag_service.py,
│                             # seo_analyzer.py, vector_store.py
│
├── data/
│   └── knowledge_base/       # 20 SEO markdown documents (380 chunks)
│
├── frontend/
│   └── streamlit_app.py      # 7-page research dashboard
│
├── scripts/
│   └── ingest_all.py         # Knowledge base ingestion script
│
├── .env.example              # Environment variable template
├── requirements.txt          # Python dependencies
└── README.md                 # Project documentation
```

---

## 🧪 Installation & Usage

### 1️⃣ Clone the repository
```
git clone https://github.com/yourusername/seo-blog-automation.git
cd seo-blog-automation
```

### 2️⃣ Create a virtual environment
```
conda create -n seo_blog_env python=3.10
conda activate seo_blog_env
```

### 3️⃣ Install dependencies
```
pip install -r requirements.txt
```

### 4️⃣ Set up environment variables
```
cp .env.example .env
```
Open `.env` and add your `GEMINI_API_KEY`

### 5️⃣ Ingest the knowledge base
```
python scripts/ingest_all.py
```

### 6️⃣ Run the backend
```
cd backend
uvicorn app.main:app --reload
```

### 7️⃣ Run the frontend *(new terminal)*
```
streamlit run frontend/streamlit_app.py
```

Open `http://localhost:8501` in your browser.

---

## 📥 Knowledge Base

The knowledge base contains 20 authoritative SEO markdown documents (380 chunks) from:
- Google Search Central
- Moz
- Ahrefs
- web.dev
- HubSpot
- Search Engine Land

Topics covered: Technical SEO, On-Page SEO, Link Building, Keyword Research,
Core Web Vitals, Schema Markup, Voice Search SEO, Mobile SEO, Content Marketing,
Local SEO, E-E-A-T, Page Speed, International SEO, Video SEO, and more.

---

## 📊 SEO Scoring Formula

| Metric | Points | Target |
|---|---|---|
| Keyword Density | 25 pts | 1.0–2.0% |
| Word Count | 25 pts | 1,000–1,800 words |
| Readability | 10 pts | Flesch Reading Ease |
| Content Structure | 28 pts | H2 + H3 heading counts |
| Keyword Placement | 12 pts | Keyword in title + first 500 chars |
| **Total** | **100 pts** | |

---

## 📈 Experimental Results

| Metric | Value |
|---|---|
| Total Experiments | 36 |
| RAG Win Rate | 94.4% (34/36) |
| Avg RAG SEO Score | 86.0 |
| Avg Baseline SEO Score | 85.5 |
| Avg SEO Improvement | +0.43 pts |
| t-Statistic | 65.67 |
| p-value | ≈ 0.0 |
| RAG Citations per Blog | 8 (avg) |
| Baseline Citations per Blog | 0 |

---

## 🛑 Important Note

This system is designed for **SEO content research and automation**.
It works best for SEO-domain keywords backed by the curated knowledge base.
Blog generation quality depends on Gemini API availability (free tier: 20 requests/day).
For production use, a paid API tier is recommended.

---

## 🧑‍💻 Author

**Ashmita Sharma**  
B.Tech — Artificial Intelligence & Data Science  
Delhi Technical Campus, Greater Noida  
Affiliated to GGSIPU, New Delhi  
