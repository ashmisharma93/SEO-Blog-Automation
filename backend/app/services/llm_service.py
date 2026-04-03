import io
import os
import time
import base64
import requests
from google import genai
from backend.app.core.config import settings

client = genai.Client(api_key=settings.GEMINI_API_KEY)

HF_IMAGE_MODEL = "black-forest-labs/FLUX.1-schnell"
HF_API_URL = f"https://api-inference.huggingface.co/models/{HF_IMAGE_MODEL}"

IMAGE_CACHE_DIR = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "..", "..", "..", "data", "image_cache"
)


def _ensure_cache_dir():
    os.makedirs(IMAGE_CACHE_DIR, exist_ok=True)


def _cache_path(cache_key: str) -> str:
    safe_key = "".join(c if c.isalnum() or c in "-_" else "_" for c in cache_key)
    return os.path.join(IMAGE_CACHE_DIR, f"{safe_key[:80]}.png")


def generate_blog_image(prompt: str, cache_key: str = None) -> str | None:
    """
    Generate a relevant AI image using Hugging Face FLUX.1-schnell.
    Returns base64-encoded PNG string, or None if generation fails.
    Caches images locally to avoid re-generating on page reload.
    """
    if not settings.HF_API_KEY:
        print("HF_API_KEY not set — skipping image generation")
        return None

    _ensure_cache_dir()

    if cache_key:
        cached = _cache_path(cache_key)
        if os.path.exists(cached):
            print(f"Using cached image for: {cache_key}")
            with open(cached, "rb") as f:
                img_bytes = f.read()
            return "data:image/png;base64," + base64.b64encode(img_bytes).decode()

    headers = {"Authorization": f"Bearer {settings.HF_API_KEY}"}
    payload = {
        "inputs": prompt,
        "parameters": {
            "width": 1024,
            "height": 512,
            "num_inference_steps": 4,
            "guidance_scale": 0.0,
        }
    }

    for attempt in range(3):
        try:
            print(f"Generating image: {prompt[:60]}... (attempt {attempt + 1})")
            response = requests.post(HF_API_URL, headers=headers, json=payload, timeout=60)

            if response.status_code == 200:
                img_bytes = response.content
                if cache_key:
                    with open(_cache_path(cache_key), "wb") as f:
                        f.write(img_bytes)
                return "data:image/png;base64," + base64.b64encode(img_bytes).decode()

            elif response.status_code == 503:
                wait_time = 20 * (attempt + 1)
                print(f"Model loading, waiting {wait_time}s...")
                time.sleep(wait_time)

            elif response.status_code == 429:
                print("HF rate limit hit — waiting 30s...")
                time.sleep(30)

            else:
                print(f"HF image API error {response.status_code}: {response.text[:200]}")
                return None

        except requests.exceptions.Timeout:
            print(f"HF image request timed out (attempt {attempt + 1})")
        except Exception as e:
            print(f"HF image generation error: {e}")
            return None

    print("Image generation failed after 3 attempts")
    return None


def build_image_prompt(keyword: str, section_heading: str = None) -> str:
    """Build a relevant image generation prompt based on blog topic."""
    base = keyword.lower().strip()

    templates = {
        "technical seo":    "professional isometric illustration of website crawling and indexing, search engine robots, sitemap structure, modern tech art, dark blue palette",
        "on page seo":      "clean infographic showing on-page SEO elements, title tags meta descriptions headings, flat design illustration",
        "link building":    "network diagram showing website backlinks and domain authority, interconnected nodes, digital marketing illustration",
        "keyword research": "data visualization of keyword analysis, search volume charts, SEO keyword mapping, professional infographic",
        "content marketing":"creative content strategy illustration, blog writing, social media, digital marketing funnel, modern flat design",
        "mobile seo":       "mobile phone with SEO optimization elements, responsive design, search rankings on smartphone, professional tech illustration",
        "local seo":        "map pin with local business search results, Google Maps, local SEO optimization illustration",
        "voice search seo": "smart speaker with voice waves and search results, voice search optimization, modern tech illustration",
        "core web vitals":  "web performance metrics dashboard, LCP FID CLS visualization, page speed optimization, professional data visualization",
        "page speed":       "website speed optimization illustration, loading progress, performance metrics, lightning bolt, professional tech art",
        "schema markup":    "structured data visualization, JSON-LD schema diagram, rich snippets in search results, professional illustration",
        "crawl budget":     "search engine crawling illustration, spider bot navigating website structure, crawl efficiency diagram",
        "image seo":        "image optimization for search engines, alt text compression visual search, professional infographic",
        "video seo":        "video content optimization for search, YouTube SEO, video schema markup, professional illustration",
        "e-e-a-t":          "trust and authority in SEO illustration, expertise authoritativeness trustworthiness, professional credibility diagram",
        "internal linking": "website internal link structure diagram, link equity flow, site architecture visualization",
        "xml sitemap":      "XML sitemap structure diagram, website page hierarchy, search engine submission, professional tech illustration",
        "international seo":"global SEO strategy illustration, hreflang tags, multilingual website, world map, professional",
        "analytics":        "SEO analytics dashboard, traffic graphs, ranking charts, Google Analytics, professional data visualization",
        "meta tags":        "HTML meta tags illustration, SEO metadata optimization, title and description tags, professional infographic",
    }

    for key, template_prompt in templates.items():
        if key in base:
            if section_heading:
                return f"{template_prompt}, section about {section_heading}, high quality, 4k, no text"
            return f"{template_prompt}, high quality, 4k, no text"

    heading_context = f", specifically about {section_heading}" if section_heading else ""
    return (
        f"professional digital marketing illustration about {keyword}{heading_context}, "
        f"SEO optimization, modern flat design, dark blue and cyan color palette, "
        f"high quality, 4k resolution, no text"
    )


# ── Gemini text generation ────────────────────────────────────────────────────

def clean_blog_output(text: str) -> str:
    """
    Post-process Gemini output to remove any HTML tags or backtick code blocks
    that slipped through despite prompt instructions.
    """
    import re
    # Remove fenced code blocks
    text = re.sub(r"```[\w]*\n?", "", text)
    text = text.replace("```", "")
    # Remove all HTML tags like <h1>, </p>, <title>, <code> etc
    text = re.sub(r"<[^>]+>", "", text)
    # Remove lone # lines
    text = re.sub(r"^#\s*$", "", text, flags=re.MULTILINE)
    # Collapse 3+ blank lines into 2
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def call_gemini_with_retry(prompt: str, retries: int = 5, wait: int = 20) -> str:
    for attempt in range(retries):
        try:
            response = client.models.generate_content(
                model="models/gemini-2.5-flash",
                contents=prompt,
                config={
                    "temperature": 0.0,
                    "max_output_tokens": 4096,
                }
            )
            return clean_blog_output(response.text) if response.text else "Blog generation failed."

        except Exception as e:
            error_str = str(e)
            retryable = (
                "503" in error_str or "UNAVAILABLE" in error_str or
                "429" in error_str or "RESOURCE_EXHAUSTED" in error_str or
                "Server disconnected" in error_str or "RemoteProtocolError" in error_str or
                "connection" in error_str.lower()
            )
            if retryable:
                if attempt < retries - 1:
                    wait_time = 30 if ("429" in error_str or "RESOURCE_EXHAUSTED" in error_str) else 15
                    print(f"Gemini issue. Retrying in {wait_time}s... (attempt {attempt + 1}/{retries})")
                    time.sleep(wait_time)
                else:
                    raise Exception(f"Gemini API failed after {retries} retries.")
            else:
                raise


def generate_seo_blog(keyword: str, context_chunks: list[str], source_metadata: list[dict] = None) -> str:
    if not context_chunks:
        return "No relevant knowledge found in the knowledge base."

    formatted_context = ""
    for i, chunk in enumerate(context_chunks, start=1):
        title = ""
        if source_metadata and i - 1 < len(source_metadata):
            title = source_metadata[i - 1].get("title", "")
        label = f"[Source: {title}]" if title else f"[Source {i}]"
        formatted_context += f"\n{label}\n{chunk}\n"

    prompt = f"""
You are an expert SEO strategist and content writer.

KNOWLEDGE SOURCES:
{formatted_context}

TASK: Write a comprehensive, authoritative SEO blog on: "{keyword}"

OUTPUT FORMAT — CRITICAL RULES (follow exactly):
- Use ONLY plain markdown. No HTML tags whatsoever. No <h1>, <h2>, <title>, <p>, <code> or any angle-bracket tags.
- Do NOT use backticks or code blocks anywhere. No ``` and no `inline code`.
- Use ## for H2 headings and ### for H3 headings only.
- Use plain hyphens (- item) for bullet points.
- Write all text as plain prose paragraphs.

STRICT STRUCTURE REQUIREMENTS:
1. First line: ## followed by the SEO-optimized blog title
2. Second line: Meta description (plain text, max 160 chars, no label prefix)
3. Introduction paragraph (150-200 words)
4. Exactly 6 sections, each starting with ## H2 heading
5. At least 4 sections must have 2 ### H3 subheadings each
6. Each section 150-250 words
7. Bullet points (- item) in at least 3 sections
8. Final section: ## Conclusion

CONTENT REQUIREMENTS:
- Total length: 1200-1600 words
- Use the keyword "{keyword}" naturally (target density: 1.5-2%)
- Cite sources inline using [Source: SourceName] notation
- Clear simple language, practical actionable tips in every section

Return ONLY the blog post. No preamble, no commentary, no HTML, no backticks.
"""
    return call_gemini_with_retry(prompt)


def generate_seo_blog_without_rag(keyword: str) -> str:
    prompt = f"""
You are an expert SEO strategist and content writer.

Write a comprehensive, authoritative SEO blog on: "{keyword}"

OUTPUT FORMAT — CRITICAL RULES (follow exactly):
- Use ONLY plain markdown. No HTML tags whatsoever. No <h1>, <h2>, <title>, <p>, <code> or any angle-bracket tags.
- Do NOT use backticks or code blocks anywhere. No ``` and no `inline code`.
- Use ## for H2 headings and ### for H3 headings only.
- Use plain hyphens (- item) for bullet points.
- Write all text as plain prose paragraphs.

STRICT STRUCTURE REQUIREMENTS:
1. First line: ## followed by the SEO-optimized blog title
2. Second line: Meta description (plain text, max 160 chars, no label prefix)
3. Introduction paragraph (150-200 words)
4. Exactly 6 sections, each starting with ## H2 heading
5. At least 4 sections must have 2 ### H3 subheadings each
6. Each section 150-250 words
7. Bullet points (- item) in at least 3 sections
8. Final section: ## Conclusion

CONTENT REQUIREMENTS:
- Total length: 1200-1600 words
- Use the keyword "{keyword}" naturally (target density: 1.5-2%)
- Clear simple language, practical actionable tips in every section

Return ONLY the blog post. No preamble, no commentary, no HTML, no backticks.
"""
    return call_gemini_with_retry(prompt)


def generate_blog_image_url(keyword: str) -> str:
    """Legacy function — kept for backward compatibility with blog_service.py."""
    return ""