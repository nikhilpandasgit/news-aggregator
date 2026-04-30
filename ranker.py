import os
import time
import logging
from collections import defaultdict
from groq import Groq
from config import GROQ_MODEL, FILTER_WEIGHT, SEMANTIC_WEIGHT, ENABLE_LLM_RERANK, RANK_BATCH_SIZE
 
logger = logging.getLogger(__name__)
 
_PROMPT = """\
You are a relevance scorer for a personal news digest. Score how relevant this article is \
to someone who follows AI, startups, tech jobs, and travel.
 
Return ONLY a single float between 0.0 and 1.0. No explanation, no preamble, no label.
 
Guidelines:
- 0.9-1.0: Breaking or highly significant news directly on topic
- 0.7-0.89: Solid, clearly on-topic article
- 0.5-0.69: Tangentially related or low-signal
- 0.0-0.49: Barely relevant or off-topic
 
Topic: {topic}
Title: {title}
Description: {description}
 
Respond with a single float only."""


class RankerAgent:
    def __init__(self):
        groq_api_key = os.getenv("GROQ_API_KEY")
        if not groq_api_key:
            raise ValueError("GROQ_API_KEY is missing")
        
        self._client = Groq(api_key=groq_api_key)

    
    def _score_article(self, article: dict, retries: int = 2) -> float:
        title = article.get("title") or ""
        description: article.get("description") or ""
        topic = article.get("_topic", "General")

        prompt = _PROMPT.format(title=title, description=description, topic=topic)

        for attempt in range(1, retries+2):
            try:
                response = self._client.chat.completions.create(
                    model=GROQ_MODEL,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.1,
                    max_tokens=10,
                )
                raw = response.choices[0].message.content.strip()
                score = float(raw)
                score = max(0.0, min(1.0, score))  # clamp to [0, 1]
                return round(score, 4)
                
            except Exception as exc:
                logger.warning(
                    "Semantic score API failed attempt %d/%d for '%s': %s",
                    attempt, retries + 1, title[:60], exc,
                )
                if attempt <= retries:
                    time.sleep(2 ** attempt)

        return 0.5
    

    def rank(self, articles: list[dict]) -> list[dict]:
        if not articles:
            return articles
        
        for i, article in enumerate(articles):
            semantic_score = self._score_article(article)
            filter_score = article.get("_score", 0.0)

            filter_score = article.get("_score", 0.0)

            final_score = round(FILTER_WEIGHT * filter_score + SEMANTIC_WEIGHT * semantic_score, 4)

            article["_semantic_score"] = semantic_score
            article["_final_score"] = final_score

            # small pause to stay within Groq rate limits
            if (i + 1) % RANK_BATCH_SIZE == 0 and i + 1 < len(articles):
                time.sleep(1)
            
        by_topic: dict[str, list[dict]] = defaultdict(list)

        for a in articles:
            by_topic[a.get("_topic", "General")].append(a)
        
        ranked: list[dict] = []
        for topic in by_topic.values():
            topic.sort(key=lambda a: a["_final_score"], reverse=True)
            ranked.extend(topic)
        
        return ranked