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

    def _call_groq(self, title: str, description: str) -> tuple[str, str]:
        prompt = _PROMPT.format(title=title, description=description)
        response = self._client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=120,
        )

        usage = response.usage
        raw = response.choices[0].message.content.strip()
        lines = [l.strip() for l in raw.splitlines() if l.strip() and l.strip() != "END"]

        if len(lines) < 2:
            raise ValueError(f"Unexpected response format: {raw!r}")

        return lines[0], lines[1]

    def summarise(self, article: dict, retries: int = 2) -> dict:
        title       = article.get("title") or ""
        description = article.get("description") or ""

        if not description.strip():
            article["_summary"] = ""
            article["_why"]     = ""
            return article

        for attempt in range(1, retries + 2):
            try:
                summary, why = self._call_groq(title, description)
                article["_summary"] = summary
                article["_why"]     = why
                logger.info("Summarised [attempt %d]: %s", attempt, title[:60])
                return article
            except Exception as exc:
                logger.warning(
                    "Summarise attempt %d/%d failed for '%s': %s",
                    attempt, retries + 1, title[:60], exc,
                )
                if attempt <= retries:
                    time.sleep(2 ** attempt)

        logger.error("Summarise gave up on '%s' — using original description", title[:60])
        article["_summary"] = ""   # empty so formatter falls back to grey description
        article["_why"]     = ""
        return article

    def summarise_batch(self, articles: list[dict]) -> list[dict]:
        for a in articles:
            a.setdefault("_summary", "")
            a.setdefault("_why", "")

        total = min(len(articles), SUMMARISE_TOP_K)

        for i, article in enumerate(articles):
            self.summarise(article=article)

        return articles