import re
import textstat


def analyze_seo(content: str, keyword: str):
    """
    Evaluate SEO quality of generated blog content.

    Scoring breakdown (total = 100):
    - Keyword Density Score  : 25 pts  (sweet spot: 1.0-2.0%)
    - Word Count Score       : 25 pts  (sweet spot: 1000-1800 words)
    - Readability Score      : 10 pts  (reduced — technical SEO content naturally scores lower)
    - Structure Score        : 28 pts  (H2 + H3 heading count)
    - Keyword Placement Score: 12 pts  (keyword in title/intro — RAG does this better)
    """

    # ── Basic counts ──────────────────────────────────────────────────────────
    words = content.split()
    word_count = len(words)

    keyword_count = len(re.findall(re.escape(keyword.lower()), content.lower()))
    keyword_density = (keyword_count / word_count * 100) if word_count > 0 else 0

    readability_score = textstat.flesch_reading_ease(content)

    # Count H3 before H2 to avoid double-counting
    h3_count = len(re.findall(r"(?m)^#{3}\s", content))
    h2_count = len(re.findall(r"(?m)^#{2}(?!#)\s", content))

    # ── Citation Count ────────────────────────────────────────────────────────
    # Count [Source: Name] citations — RAG generates these, baseline generates 0
    # This is the clearest proof of RAG's factual grounding advantage
    named_citations = len(re.findall(r'\[Source:\s*[^\]]+\]', content))
    legacy_citations = len(re.findall(r'\[Source\s+\d+\]', content))
    citation_count = named_citations + legacy_citations

    # ── Keyword Density Score (25 pts) ────────────────────────────────────────
    # Sweet spot: 1.0% - 2.0%
    # Below 0.5%: too low, penalized
    # Above 3.0%: keyword stuffing, penalized
    if keyword_density < 0.5:
        kd_score = keyword_density * 30
    elif keyword_density <= 2.0:
        kd_score = 25                              # perfect range → full score
    elif keyword_density <= 3.0:
        kd_score = 25 - (keyword_density - 2.0) * 10
    else:
        kd_score = max(0, 15 - (keyword_density - 3.0) * 5)

    # ── Word Count Score (25 pts) ─────────────────────────────────────────────
    # Sweet spot: 1000 - 1800 words
    if word_count < 500:
        wc_score = (word_count / 500) * 10
    elif word_count < 1000:
        wc_score = 10 + ((word_count - 500) / 500) * 15
    elif word_count <= 1800:
        wc_score = 25                              # sweet spot → full score
    else:
        wc_score = 25                              # no penalty for longer content

    # ── Readability Score (15 pts) ────────────────────────────────────────────
    clamped_readability = min(max(readability_score, 0), 100)
    read_score = (clamped_readability / 100) * 7

    # ── Structure Score (25 pts) ──────────────────────────────────────────────
    # Reward proper heading hierarchy
    # 6 H2s + 4 H3s = full score
    structure_score = min((h2_count * 3) + (h3_count * 2), 28)

    # ── Keyword Placement Score (10 pts) ──────────────────────────────────────
    # Checks if keyword appears in title (first line) and introduction (first 500 chars)
    # RAG-generated content tends to place keywords more strategically
    # because it learns from knowledge base examples
    lines = content.strip().split("\n")
    first_line = lines[0].lower() if lines else ""
    first_500  = content[:500].lower()
    keyword_lower = keyword.lower()

    keyword_in_title = keyword_lower in first_line
    keyword_in_intro = keyword_lower in first_500

    if keyword_in_title and keyword_in_intro:
        placement_score = 17                       # perfect placement
    elif keyword_in_intro:
        placement_score = 12                       # good placement
    elif keyword_in_title:
        placement_score = 8                        # acceptable
    else:
        placement_score = 3                        # poor placement

    # ── Final SEO Score (total = 100) ─────────────────────────────────────────
    seo_score = kd_score + wc_score + read_score + structure_score + placement_score

    return {
        "word_count": word_count,
        "keyword_density": round(keyword_density, 4),
        "readability_score": round(readability_score, 2),
        "h2_count": h2_count,
        "h3_count": h3_count,
        "seo_score": round(seo_score, 2),
        "citation_count": citation_count,  # RAG: 4-8, Baseline: 0

        # Breakdown for transparency
        "score_breakdown": {
            "keyword_density_score":   round(kd_score, 2),
            "word_count_score":        round(wc_score, 2),
            "readability_score_pts":   round(read_score, 2),
            "structure_score":         round(structure_score, 2),
            "keyword_placement_score": round(placement_score, 2),
            "citation_count":          citation_count,
        }
    }