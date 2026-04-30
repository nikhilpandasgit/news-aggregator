import os
import logging
from datetime import datetime, timezone, timedelta
from supabase import create_client, Client

logger = logging.getLogger(__name__)

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_ANON_KEY")
IS_PRODUCTION = os.getenv("PRODUCTION") == 'true'


def init_db():
    logger.info("Supabase connected.")

def get_client() -> Client:
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_ANON_KEY")

    if not url:
        raise ValueError("SUPABASE_URL is missing")
    if not key:
        raise ValueError("SUPABASE_ANON_KEY is missing")

    return create_client(url, key)


# Save each run to `runs` table
def save_run(run_id: str, article_count: int, topics: list[str]) -> None:
    now = datetime.now(timezone.utc).isoformat()
    supabase = get_client()
    
    supabase.table("runs").insert({
        "run_id": run_id,
        "ran_at": now,
        "article_count": article_count,
        "topics": ", ".join(topics),
        "is_production": IS_PRODUCTION
    }).execute()
    
    logger.info("Run %s logged - %d articles", run_id, article_count)


# save articles per run to `articles` table
def save_articles(articles: list[dict], run_id: str) -> list[dict]:
    now = datetime.now(timezone.utc).isoformat()
    supabase = get_client()
    
    rows = [
        {
            "run_id": run_id,
            "url": a.get("url", ""),
            "title": a.get("title", ""),
            "source": (a.get("source") or {}).get("name", ""),
            "topic": a.get("_topic", "General"),
            "score": a.get("_score", 0.0),
            "delivered_at": now,
        }for a in articles
    ]
    
    res = supabase.table("articles").insert(rows).execute()
    inserted = res.data

    logger.info("Saved %d articles (run %s)", len(rows), run_id)
    return inserted


# Save per-article ranking scores
def save_article_scores(articles: list[dict], inserted_articles: list[dict], run_id: str) -> None:
    supabase = get_client()
    now = datetime.now(timezone.utc).isoformat()

    # "url": "id" lookup for the inserted articles
    url_to_id: dict[str, int] = {
        row["url"] : row["id"]
        for row in inserted_articles
        if row.get("url") and row.get("id")
    }

    rows = []
    for a in articles:
        article_id = url_to_id.get(a.get("url", ""))
        if not article_id:
            logger.warning("No article_id found for url: %s — skipping score row", a.get("url"))
            continue

        rows.append({
            "article_id": article_id,
            "run_id": run_id,
            "topic": a.get("_topic", "General"),
            "filter_score": a.get("_score", 0.0),
            "semantic_score": a.get("_semantic_score"),
            "final_score": a.get("_final_score", a.get("_score", 0.0)),
            "published_at": a.get("publishedAt"),
            "created_at": now,
        })

        if rows:
            supabase.table("article_scores").insert(rows).execute()
            logger.info("Saved %d article scores (run %s)", len(rows), run_id)


# fetch delivered URLs from the past week to avoid duplicates
def get_seen_urls() -> set[str]:
    supabase = get_client()
    one_week_ago = (datetime.now(timezone.utc) - timedelta(days=3)).isoformat()
    
    res = supabase.table("articles").select("url").gt("delivered_at", one_week_ago).execute()
    urls = {row["url"] for row in res.data}
    
    logger.info("Fetched %d seen URLs from the past week", len(urls))
    return urls


# Return titles delivered in the last N days, for cross-run title dedup.
def get_recent_titles(days: int = 3) -> list[str]:
    cutoff = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
    supabase = get_client()
    res = (
        supabase.table("articles")
        .select("title")
        .gte("delivered_at", cutoff)
        .execute()
    )
    return [row["title"] for row in res.data if row.get("title")]