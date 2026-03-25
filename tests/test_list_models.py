from google import genai
from backend.app.core.config import settings

client = genai.Client(api_key=settings.GEMINI_API_KEY)
models = client.models.list()

for m in models:
    print(m.name)