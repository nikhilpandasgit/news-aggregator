# 📰 Personal News Agent

A self-hosted, AI-powered news digest built for myself. Just the topics I care about — curated, deduplicated, and summarised — delivered to my inbox twice a day.

## What it does

Every day at **7:00 AM** and **7:00 PM**, this agent automatically:

1. Fetches fresh articles from NewsAPI across four topics: **AI & LLMs**, **Startups & Funding**, **Jobs & Hiring**, and **Travel & Nomad**
2. Scores each article for relevance using a hybrid scoring system (TF-IDF + keyword match + recency), filtering out low-quality sources via a domain blocklist and a minimum score threshold
3. Deduplicates against the last 3 days of articles stored in Supabase, using title similarity to avoid near-duplicate stories
4. Summarises the top 6 articles using **Groq's `llama-3.3-70b-versatile`** model via a `SummariserAgent`, with token usage logged per run
5. Formats a clean HTML email grouped by topic, AI-generated summaries appear as an indigo callout, with a plain description fallback for unsummarised articles
6. Sends it straight to my inbox via Gmail SMTP
