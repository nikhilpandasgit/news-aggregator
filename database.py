import os
import logging
from datetime import datetime, timezone, timedelta
from supabase import create_client, Client

logger = logging.getLogger(__name__)

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_ANON_KEY")
IS_PRODUCTION = os.getenv("PRODUCTION") == 'true'

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


def init_db():
    logger.info("Supabase connected.")


# Save each run to `runs` table
def save_run(run_id: str, article_count: int, topics: list[str]) -> None:
    now = datetime.now(timezone.utc).isoformat()
    
    supabase.table("runs").insert({
        "run_id": run_id,
        "ran_at": now,
        "article_count": article_count,
        "topics": ", ".join(topics),
        "is_production": IS_PRODUCTION
    }).execute()
    
    logger.info("Run %s logged - %d articles", run_id, article_count)


# save articles per run to `articles` table
def save_articles(articles: list[dict], run_id: str) -> None:
    now = datetime.now(timezone.utc).isoformat()
    
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
    
    logger.info("Saved %d articles (run %s)", len(rows), run_id)