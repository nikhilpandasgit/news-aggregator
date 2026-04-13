import logging
import sys
from collections import Counter
from dotenv import load_dotenv
load_dotenv()

from config import KEYWORDS, MAX_ARTICLES
from fetcher import fetch_articles
from filter import filter_articles
from formatter import format_digest
from email_sender import send_email

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%H:%M:%S",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)


def run():
    logger.info("Starting news agent")

    # 1. fetch
    try:
        articles = fetch_articles()
    except Exception as exc:
        logger.error("Fetch failed: %s", exc)

    if not articles:
        logger.warning("No articles returned, check FETCH_TERMS or API quota.")
        return

    # 2. score & filter
    try:
        articles = filter_articles(articles, KEYWORDS)
    except Exception as exc:
        logger.error("Filtering failed: %s", exc)

    if not articles:
        logger.warning("No articles matched keywords, adjust KEYWORDS in config.py.")
        return

    # 3. format
    try:
        subject, html = format_digest(articles)
    except Exception as exc:
        logger.error("Formatting failed: %s", exc)

    # 4. send
    try:
        send_email(subject, html)
        logger.info("Digest sent.")
    except Exception as exc:
        logger.error("Email failed: %s", exc)

if __name__ == "__main__":
    run()