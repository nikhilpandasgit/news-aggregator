import os
import requests
from config import FETCH_TERMS

def fetch_articles(max_results: int = 40) -> list[dict]:
    api_key = os.getenv("NEWS_API_KEY")
    query = " OR ".join(f'"{term}"' for term in FETCH_TERMS)

    resp = requests.get(
        "https://newsapi.org/v2/everything",
        params={
            "q": query,
            "language": "en",
            "sortBy": "publishedAt",
            "pageSize": max_results,
            "apiKey": api_key,
        },
        timeout=10,
    )
    resp.raise_for_status()
    print(resp.json())
    return resp.json().get("articles", [])