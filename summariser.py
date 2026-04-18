import os
import time
import logging
from groq import Groq
from config import GROQ_MODEL, SUMMARISE_TOP_K

logger = logging.getLogger(__name__)

_PROMPT = """\
You are a concise news summariser. Given an article title and description, return exactly 3 lines:
Line 1: A 1-2 sentence summary of what the article is about.
Line 2: A 1 sentence explanation of why this matters to someone interested in AI, startups, tech jobs, or travel.
Line 3: Write only the word END.

Title: {title}
Description: {description}

Respond with nothing else — no labels, no markdown, no preamble."""

class SummariserAgent:
    def __init__(self):
        groq_api_key = os.getenv("GROQ_API_KEY")
        if not groq_api_key:
            raise ValueError("GROQ_API_KEY is missing")
        self._client = Groq(api_key=groq_api_key)
    
    # Call groq api for (summary, why it matters)
    def _call_groq(self) -> tuple[str, str]:
        title="How does OpenAI’s Agents SDK sandboxing work? #tech"
        description="OpenAI updates Agents SDK for safer, in house agent testing OpenAI has released an update to its Agents SDK focused on security and operational reliability for agentic AI systems. The new version adds native sandboxing and an in distribution harness intended …"
        prompt = _PROMPT.format(title=title, description=description)
        response = self._client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[{"role" : "user", "content": prompt}],
            temperature=0.3,
            max_tokens=120
        )

        print(response.json())
