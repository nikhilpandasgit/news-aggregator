def score_article(article: dict, keywords: list[str]) -> int:
    title = (article.get("title") or "").lower()
    desc = (article.get("description") or "").lower()
    score = 0

    for kw in keywords:
        kw = kw.lower()
        is_phrase = len(kw.split()) > 1  # e.g. "artificial intelligence"

        title_hits = title.count(kw)
        desc_hits = desc.count(kw)

        if title_hits:
            score += title_hits * (5 if is_phrase else 3)
        if desc_hits:
            score += desc_hits * (3 if is_phrase else 1)

    return score


def filter_articles(articles: list[dict], keywords: list[str]) -> list[dict]:
    seen_urls = set()
    scored = []

    for article in articles:
        url = article.get("url", "")
        if url in seen_urls:
            continue
        seen_urls.add(url)

        s = score_article(article, keywords)
        if s > 0:
            article["_score"] = s
            scored.append(article)

    scored.sort(key=lambda a: a["_score"], reverse=True)
    return scored