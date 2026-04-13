import os
import logging
import requests
from config import FETCH_TERMS_BY_TOPIC, TITLE_SCOPED_TERMS, ARTICLES_PER_TOPIC

logger = logging.getLogger(__name__)

# Build query to send in request
def _build_query(terms: list[str]) -> str:
    title_terms     = [t for t in terms if t in TITLE_SCOPED_TERMS]
    any_field_terms = [t for t in terms if t not in TITLE_SCOPED_TERMS]

    parts = []
    if title_terms:
        parts.append(" OR ".join(f'intitle:"{t}"' for t in title_terms))
    if any_field_terms:
        parts.append(" OR ".join(f'"{t}"' for t in any_field_terms))

    return " OR ".join(f"({p})" for p in parts)

# Fetch articles for one topic
def _fetch_topic(api_key: str, topic: str, terms: list[str]) -> list[dict]:
    query = _build_query(terms)

    try:
        resp = requests.get(
            "https://newsapi.org/v2/everything",
            params={
                "q":        query,
                "language": "en",
                "sortBy":   "publishedAt",
                "pageSize": ARTICLES_PER_TOPIC,
                "apiKey":   api_key,
            },
            timeout=10,
        )
        resp.raise_for_status()
        articles = resp.json().get("articles", [])
        return articles

    except requests.RequestException as exc:
        logger.warning("Failed to fetch '%s': %s — skipping", topic, exc)
        return []

# Combine all fetched articles for all topics
def fetch_articles() -> list[dict]:
    api_key = os.getenv("NEWS_API_KEY")
    all_articles: list[dict] = []

    for topic, terms in FETCH_TERMS_BY_TOPIC.items():
        all_articles.extend(_fetch_topic(api_key, topic, terms))

    logger.info("Fetched %d total articles across %d topics", len(all_articles), len(FETCH_TERMS_BY_TOPIC))
    return all_articles