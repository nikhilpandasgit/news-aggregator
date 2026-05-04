from datetime import datetime, timezone
import logging
import sys
from collections import Counter
from dotenv import load_dotenv
load_dotenv()

from config import KEYWORDS, MAX_ARTICLES, TITLE_SIMILARITY_THRESHOLD, ENABLE_LLM_RERANK
from fetcher import fetch_articles
from filter import filter_articles, _jaccard
from formatter import format_digest
from email_sender import send_email
from database import init_db, save_articles, save_run, get_seen_urls, get_recent_titles, save_article_scores
from summariser import SummariserAgent
from ranker import RankerAgent

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%H:%M:%S",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)


# re-run for articles in db in the past week
def _cross_run_dedup_by_title(
    articles: list[dict],
    past_titles: list[str],
) -> list[dict]:
    result = []
    for article in articles:
        title = article.get("title") or ""
        if not any(_jaccard(title, past) >= TITLE_SIMILARITY_THRESHOLD for past in past_titles):
            result.append(article)

    return result    


def run():
    logger.info("Starting news agent")
    
    init_db()
    run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")

    # 1. fetch
    try:
        articles = fetch_articles()
    except Exception as exc:
        logger.error("Fetch failed: %s", exc)
        return

    if not articles:
        logger.warning("No articles returned, check FETCH_TERMS or API quota.")
        return

    
    # 2. cross-run URL dedup against supabase records from the past week
    try:
        seen_urls = get_seen_urls()
        articles = [a for a in articles if (a.get("url") or "") not in seen_urls]

    except Exception as exc:
        logger.error("Cross-run URL dedup failed: %s", exc)

    
    # 3. cross-run title dedup against supabase records from the past week
    try:
        seen_titles = get_recent_titles(days=3)
        articles = _cross_run_dedup_by_title(articles, seen_titles)

    except Exception as exc:
        logger.error("Cross-run title dedup failed: %s", exc)

    if not articles:
        logger.warning("All articles already delivered recently.")
        return


    # 4. score & filter
    try:
        articles = filter_articles(articles, KEYWORDS)
    except Exception as exc:
        logger.error("Filtering failed: %s", exc)
        return
    if not articles:
        logger.warning("No articles returned from filter")
        return

    # 5. Semantic Ranking filtered articles using LLM
    if ENABLE_LLM_RERANK:
        try:
            ranker = RankerAgent()
            articles = ranker.rank(articles)
            logger.info("ranking complete.")
        except ValueError as exc:
            logger.warning("RankerAgent init failed: %s", exc)
        except Exception as exc:
            logger.error("Ranking failed: %s", exc)
    else:
        for a in articles:
            a["_final_score"] = a.get("_score", 0.0)
            a["_semantic_score"] = None


    # 6. Summariser call
    try:        
        summariser = SummariserAgent()
    except ValueError as exc:
        summariser = None
        
    if summariser:
        try:
            articles = summariser.summarise_batch(articles=articles)
            logger.info("Summarisation complete")
        except Exception as exc:
            logger.error("Summarisation failed: %s", exc)


    # 7. format
    try:
        subject, html = format_digest(articles)
    except Exception as exc:
        logger.error("Formatting failed: %s", exc)
        return

    # 8. send email
    try:
        send_email(subject, html)
        logger.info("Digest sent.")
    except Exception as exc:
        logger.error("Email failed: %s", exc)
        return
        
    # 9. Update delivered articles in database
    topics = list({a.get("_topic", "General") for a in articles})
    save_run(run_id, len(articles), topics)
    inserted_articles = save_articles(articles, run_id)

    try:
        save_article_scores(articles, inserted_articles, run_id)
    except Exception as exc:
        logger.error("Failed to save article scores: %s", exc)

if __name__ == "__main__":
    run()