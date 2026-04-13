# 📰 Personal News Agent
 
A lightweight, self-hosted news aggregator built for myself. Just the topics I care about, delivered to my inbox twice a day.
 
## What it does
 
Every day at **7:00 AM** and **7:00 PM**, this agent automatically:

1. Fetches fresh articles from NewsAPI across my chosen topics
2. Scores each article for relevance using a hybrid scoring system (TF-IDF + keyword + recency)
3. Picks the best articles sorted by scores.
4. Formats them into a clean HTML email grouped by topic
5. Sends it straight to my inbox via Gmail SMTP
