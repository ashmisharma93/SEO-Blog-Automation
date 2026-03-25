import time
from google import genai
from backend.app.core.config import settings

client = genai.Client(api_key=settings.GEMINI_API_KEY)


def call_gemini_with_retry(prompt: str, retries: int = 5, wait: int = 20) -> str:
    """
    Call Gemini with automatic retry on all transient errors.
    Handles: 503 server overload, 429 rate limit, connection drops.
    """
    for attempt in range(retries):
        try:
            response = client.models.generate_content(
                model="models/gemini-2.5-flash",
                contents=prompt
            )
            return response.text if response.text else "Blog generation failed."

        except Exception as e:
            error_str = str(e)

            retryable = (
                "503" in error_str or
                "UNAVAILABLE" in error_str or
                "429" in error_str or
                "RESOURCE_EXHAUSTED" in error_str or
                "Server disconnected" in error_str or
                "RemoteProtocolError" in error_str or
                "connection" in error_str.lower()
            )

            if retryable:
                if attempt < retries - 1:
                    wait_time = 30 if ("429" in error_str or "RESOURCE_EXHAUSTED" in error_str) else 15
                    print(f"Gemini issue. Retrying in {wait_time}s... (attempt {attempt + 1}/{retries})")
                    time.sleep(wait_time)
                else:
                    raise Exception(
                        f"Gemini API failed after {retries} retries. "
                        "Please wait a few minutes and try again."
                    )
            else:
                raise


def generate_seo_blog(keyword: str, context_chunks: list[str], source_metadata: list = None) -> str:
    """
    Generate structured SEO blog using RAG with citations.
    Uses knowledge sources to enhance and ground content.
    """
    if not context_chunks:
        return "No relevant knowledge found in the knowledge base."

    formatted_context = ""
    source_labels = []
    seen_labels = {}
    for i, chunk in enumerate(context_chunks, start=1):
        if source_metadata and i-1 < len(source_metadata):
            meta = source_metadata[i-1]
            raw_source = meta.get("source", "")
            title = meta.get("title", "SEO Knowledge Base")
            if raw_source and raw_source not in ("unknown", ""):
                label = raw_source.split(",")[0].strip()[:40]
            else:
                label = title.split(":")[0].strip()[:40]
            if label in seen_labels:
                seen_labels[label] += 1
                label = label + " (" + str(seen_labels[label]) + ")"
            else:
                seen_labels[label] = 1
            source_labels.append(label)
            formatted_context += "\n[Source: " + label + "]\n" + chunk + "\n"
        else:
            label = "Source " + str(i)
            source_labels.append(label)
            formatted_context += "\n[Source " + str(i) + "]\n" + chunk + "\n"

    source_list = "\n".join(["  " + str(i+1) + ". " + lbl for i, lbl in enumerate(source_labels)])

    prompt = f"""
You are an expert SEO strategist and content writer.

You have been provided with expert knowledge sources below.
Use them to ENHANCE and GROUND your writing with specific facts,
best practices, and domain expertise from these sources.

KNOWLEDGE SOURCES:
{formatted_context}

TASK:
Write a comprehensive, authoritative SEO blog on: "{keyword}"

STRICT STRUCTURE REQUIREMENTS (you MUST follow these exactly):
1. Start with an SEO optimized title using ## heading
2. Write a meta description line (max 160 characters)
3. Write an introduction paragraph (150-200 words)
4. Write EXACTLY 6 sections each with a ## H2 heading
5. Under at least 4 of those sections add 2 ### H3 subheadings
6. Each section must be 150-250 words
7. Use bullet points or numbered lists in at least 3 sections
8. End with a ## Conclusion section

CONTENT REQUIREMENTS:
- Total length: 1200-1600 words
- Use the keyword "{keyword}" naturally throughout (target density: 1.5-2%)
- Cite knowledge sources using [Source: SourceName] notation where relevant
- Write in clear simple language (short sentences, avoid jargon)
- Include practical actionable tips in every section

IMPORTANT: The ## and ### headings are mandatory for SEO scoring.
Do not skip headings or merge sections.

Return only the final blog post with no extra commentary.
"""
    return call_gemini_with_retry(prompt)


def generate_seo_blog_without_rag(keyword: str) -> str:
    """
    Baseline blog generation without RAG context.
    Uses identical structure requirements for fair comparison.
    """
    prompt = f"""
You are an expert SEO strategist and content writer.

Write a comprehensive, authoritative SEO blog on: "{keyword}"

STRICT STRUCTURE REQUIREMENTS (you MUST follow these exactly):
1. Start with an SEO optimized title using ## heading
2. Write a meta description line (max 160 characters)
3. Write an introduction paragraph (150-200 words)
4. Write EXACTLY 6 sections each with a ## H2 heading
5. Under at least 4 of those sections add 2 ### H3 subheadings
6. Each section must be 150-250 words
7. Use bullet points or numbered lists in at least 3 sections
8. End with a ## Conclusion section

CONTENT REQUIREMENTS:
- Total length: 1200-1600 words
- Use the keyword "{keyword}" naturally throughout (target density: 1.5-2%)
- Write in clear simple language (short sentences, avoid jargon)
- Include practical actionable tips in every section

IMPORTANT: The ## and ### headings are mandatory for SEO scoring.
Do not skip headings or merge sections.

Return only the final blog post with no extra commentary.
"""
    return call_gemini_with_retry(prompt)


def generate_blog_image_url(keyword: str) -> str:
    """
    Generate a relevant image URL for the blog using Pollinations AI.
    Free, no API key required.
    """
    import urllib.parse
    prompt = f"professional blog header image about {keyword}, digital marketing, SEO, modern flat design"
    encoded = urllib.parse.quote(prompt)
    return f"https://image.pollinations.ai/prompt/{encoded}?width=1200&height=400&nologo=true"