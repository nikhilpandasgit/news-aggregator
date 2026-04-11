from dotenv import load_dotenv
load_dotenv()

from config import KEYWORDS, MAX_ARTICLES, MAX_IN_DIGEST
from fetcher import fetch_articles
from filter import filter_articles
from email_sender import send_email
from formatter import format_digest

def run():
    try:
        articles = fetch_articles(MAX_ARTICLES)
        articles = filter_articles(articles, KEYWORDS)
        articles = articles[:MAX_IN_DIGEST]

        if not articles:
            print("No matching articles. No email sent.")
            return

        subject, html = format_digest(articles)
        send_email(subject, html)
        
    except Exception as e:
        print(f"Exception Occured: {e}")

if __name__ == "__main__":
    run()