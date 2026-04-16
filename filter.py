import math
import re
from datetime import datetime, timezone
from collections import Counter, defaultdict
from config import KEYWORD_TOPICS, MAX_PER_TOPIC, MIN_DESCRIPTION_LENGTH


# strip punctuation and split into tokens, returns a list of tokenized articles
def _tokenise(text: str) -> list[str]:
    return re.findall(r"[a-z0-9]+", text.lower())


# Jaccard similarity between two sets of tokens
def _jaccard(a: str, b: str) -> float:
    sa, sb = set(_tokenise(a)), set(_tokenise(b))
    if not sa or not sb:
        return 0.0
    return len(sa & sb) / len(sa | sb)



# dedup by title similarity (Jaccard > 0.4) to catch redundant articles with different URLs
def _deduplicate_by_title(articles: list[dict], threshold: float = 0.4) -> list[dict]:
    kept: list[dict] = []
    for article in articles:
        title = article.get("title") or ""
        if not any(_jaccard(title, k.get("title") or "") >= threshold for k in kept):
            kept.append(article)
    return kept


# compute TF-IDF scores for every article against all articles, returns a dict per article with tfidf score
def _build_tfidf_scores(articles: list[dict]) -> list[dict[str, float]]:
    N = len(articles)
    if N == 0:
        return []
    
    # tokenize the title and description of each article
    corpora: list[list[str]] = []
    for a in articles:
        text = f"{a.get('title') or ''} {a.get('description') or ''}"
        corpora.append(_tokenise(text))
    
    # document frequency (how many articles contain each term)
    df: dict[str, int] = Counter()
    for tokens in corpora:
        for term in set(tokens):
            df[term] += 1
    
    # TF-IDF scores per article
    tfidf_list: list[dict[str, float]] = []
    for tokens in corpora:
        tf = Counter(tokens)
        total = len(tokens) or 1
        scores: dict[str, float] = {}

        for term, count in tf.items():
            term_tf = count / total
            term_idf = math.log((N + 1) / (df[term] + 1)) + 1
            scores[term] = term_tf * term_idf
        tfidf_list.append(scores)

    return tfidf_list


# A multiplier that boosts newer articles (value between 1.0 to 0.5)
def _recency_factor(published_at: str | None) -> float:
    if not published_at:
        return 0.75  # neutral score for unknown time
    
    try:
        pub = datetime.fromisoformat(published_at.replace("Z", "+00:00"))
        now = datetime.now(timezone.utc)
        age_hours = (now - pub).total_seconds() / 3600
    except (ValueError, TypeError):
        return 0.75
    
    if age_hours <= 6:
        return 1.0
    if age_hours >= 48:
        return 0.5

    # A linearly decaying score for articles between 6hrs to 48 hrs
    return 1.0 - 0.5 * (age_hours - 6) / 42


# Returns a multiplier based on content shape.
def _content_quality_score(article: dict) -> float:
    score = 1.0

    desc   = article.get("description") or ""
    title  = article.get("title") or ""
    author = article.get("author") or ""

    desc_len = len(desc.strip())
    if desc_len < 40:
        score *= 0.2
    elif desc_len < MIN_DESCRIPTION_LENGTH:
        score *= 0.6
    elif desc_len < 120:
        score *= 0.85

    # version-number pattern in title: "packagename 0.1.1", "v2.3.4"
    if re.search(r'\bv?\d+\.\d+(\.\d+)?\b', title):
        if desc_len >= 120:
            score *= 0.6
        else:
            score *= 0.4

    if not author.strip():
        score *= 0.8

    return round(score, 3)


# Return the most relevant topic label for an article
def _assign_topic(article: dict, keywords: list[str]) -> str:
    text = f"{article.get('title') or ''} {article.get('description') or ''}".lower()
    topic_hits: dict[str, int] = Counter()

    for kw in keywords:
        if kw.lower() in text:
            topic = KEYWORD_TOPICS.get(kw.lower(), "General")
            topic_hits[topic] += 1

    if not topic_hits:
        return "General"
    return topic_hits.most_common(1)[0][0]


# Hybrid Scoring = 50% keyword_score + 30% tfidf_score + 20% recency * content_quality
def score_article(
    article: dict,
    keywords: list[str],
    tfidf_scores: dict[str, float],
    recency: float
) -> float:

    title = (article.get("title") or "").lower()
    desc  = (article.get("description") or "").lower()
    kw_score = 0.0

    # calculate keyword score for the article
    for kw in keywords:
        kw = kw.lower()
        is_phrase = len(kw.split()) > 1

        title_hits = title.count(kw)
        desc_hits  = desc.count(kw)

        if title_hits:
            kw_score += title_hits * (5 if is_phrase else 3)
        if desc_hits:
            kw_score += desc_hits * (3 if is_phrase else 1)

    # divide by 20.0 to normalise into 0.0 - 1.0 range
    kw_norm = min(kw_score / 20.0, 1.0)

    # TF-IDF score for the article
    tfidf_sum = sum(
        tfidf_scores.get(token, 0.0)
        for kw in keywords
        for token in _tokenise(kw)
    )
    tfidf_norm = min(tfidf_sum / 0.5, 1.0)

    # base combined score
    combined = (kw_norm * 0.5) + (tfidf_norm * 0.3) + (recency * 0.2)

    # content quality multiplier
    quality = _content_quality_score(article)
    return round(combined * quality, 4)


# After scoring, enforcing a per-topic cap so no single topic floods the digest
def _cap_by_topic(articles: list[dict], max_per_topic: int) -> list[dict]:
    counts: dict[str, int] = defaultdict(int)
    result: list[dict] = []
    for a in articles:
        topic = a.get("_topic", "General")
        if counts[topic] < max_per_topic:
            counts[topic] += 1
            result.append(a)
    return result


# Deduplicate, score, assign topics, cap per topic, and sort by descending score.
def filter_articles(articles: list[dict], keywords: list[str]) -> list[dict]:
    seen_urls: set[str] = set()
    unique: list[dict] = []

    # deduplicate by URL
    for article in articles:
        url = article.get("url") or ""
        if url and url not in seen_urls:
            seen_urls.add(url)
            unique.append(article)
    
    # remove articles from blocked domains
    unique = [
        a for a in unique
        if urlparse(a.get("url") or "").netloc.lstrip("www.") not in BLOCKED_DOMAINS
    ]

    # Remove articles from blocked sources
    unique = [
        a for a in unique
        if (a.get("source") or {}).get("name", "") not in BLOCKED_SOURCE_NAMES
    ]

    # deduplicate by title similarity
    unique = _deduplicate_by_title(unique)

    if not unique:
        return []
    
    # build tfidf scores across the full unique corpus
    tfidf_list = _build_tfidf_scores(unique)

    # score each article
    scored: list[dict] = []
    for article, tfidf_scores in zip(unique, tfidf_list):
        recency = _recency_factor(article.get("publishedAt"))
        score   = score_article(article, keywords, tfidf_scores, recency)

        # require at least one keyword hit in title or description
        title = (article.get("title") or "").lower()
        desc  = (article.get("description") or "").lower()
        has_keyword_hit = any(kw.lower() in title or kw.lower() in desc for kw in keywords)

        if has_keyword_hit:
            article["_score"]   = score
            article["_recency"] = recency
            article["_topic"]   = _assign_topic(article, keywords)
            scored.append(article)

    # sort best-first, then per-topic cap
    scored.sort(key=lambda a: a["_score"], reverse=True)
    return _cap_by_topic(scored, MAX_PER_TOPIC)