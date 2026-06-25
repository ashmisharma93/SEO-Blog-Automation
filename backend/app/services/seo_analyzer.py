import re
import textstat


def analyze_seo(content: str, keyword: str):
    """
    Evaluate SEO quality of generated blog content.

    Scoring breakdown:
    - Keyword density: 25 points
    - Word count: 25 points
    - Readability: 10 points
    - Content structure: 28 points
    - Keyword placement: 12 points
    """

    words = content.split()
    word_count = len(words)

    keyword_count = len(re.findall(re.escape(keyword.lower()), content.lower()))
    keyword_density = (keyword_count / word_count * 100) if word_count > 0 else 0

    readability_score = textstat.flesch_reading_ease(content)

    h3_count = len(re.findall(r"(?m)^#{3}\s", content))
    h2_count = len(re.findall(r"(?m)^#{2}(?!#)\s", content))

    named_citations = len(re.findall(r"\[Source:\s*[^\]]+\]", content))
    legacy_citations = len(re.findall(r"\[Source\s+\d+\]", content))
    citation_count = named_citations + legacy_citations

    if keyword_density < 0.5:
        kd_score = keyword_density * 30
    elif keyword_density <= 2.0:
        kd_score = 25
    elif keyword_density <= 3.0:
        kd_score = 25 - (keyword_density - 2.0) * 10
    else:
        kd_score = max(0, 15 - (keyword_density - 3.0) * 5)

    if word_count < 500:
        wc_score = (word_count / 500) * 10
    elif word_count < 1000:
        wc_score = 10 + ((word_count - 500) / 500) * 15
    else:
        wc_score = 25

    clamped_readability = min(max(readability_score, 0), 100)
    read_score = (clamped_readability / 100) * 10

    structure_score = min((h2_count * 3) + (h3_count * 2), 28)

    lines = content.strip().split("\n")
    first_line = lines[0].lower() if lines else ""
    first_500 = content[:500].lower()
    keyword_lower = keyword.lower()

    keyword_in_title = keyword_lower in first_line
    keyword_in_intro = keyword_lower in first_500

    if keyword_in_title and keyword_in_intro:
        placement_score = 12
    elif keyword_in_intro:
        placement_score = 9
    elif keyword_in_title:
        placement_score = 6
    else:
        placement_score = 3

    seo_score = kd_score + wc_score + read_score + structure_score + placement_score

    return {
        "word_count": word_count,
        "keyword_density": round(keyword_density, 4),
        "readability_score": round(readability_score, 2),
        "h2_count": h2_count,
        "h3_count": h3_count,
        "seo_score": round(min(seo_score, 100), 2),
        "citation_count": citation_count,
        "score_breakdown": {
            "keyword_density_score": round(kd_score, 2),
            "word_count_score": round(wc_score, 2),
            "readability_score_pts": round(read_score, 2),
            "structure_score": round(structure_score, 2),
            "keyword_placement_score": round(placement_score, 2),
            "citation_count": citation_count,
        },
    }
