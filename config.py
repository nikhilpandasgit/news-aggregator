FETCH_TERMS_BY_TOPIC: dict[str, list[str]] = {
    "AI & LLMs": [
        "AI",
        "LLM",
        "generative AI",
        "artificial intelligence",
        "ChatGPT",
        "OpenAI",
        "Anthropic",
    ],
    "Startups & Funding": [
        "startup",
        "funding round",
        "series A",
        "series B",
    ],
    "Jobs & Hiring": [
        "remote job",
        "tech hiring",
    ],
    "Travel & Nomad": [
        "solo travel",
        "digital nomad",
    ],
}

TITLE_SCOPED_TERMS: set[str] = {"AI", "LLM", "generative AI"}


KEYWORDS: list = [
    # AI
    "artificial intelligence",
    "AI agents",
    "large language model",
    "LLM",
    "generative AI",
    "ChatGPT",
    "OpenAI",
    "Anthropic",

    # Startups & companies
    "startup",
    "funding round",
    "series A",
    "series B",
    "acquisition",

    # Jobs
    "remote job",
    "tech hiring",
    "software engineer",
    "job opportunity",

    # Solo travel
    "solo travel",
    "digital nomad",
    "budget travel",
    "travel guide",
]

KEYWORD_TOPICS: dict[str, str] = {
    "artificial intelligence": "AI & LLMs",
    "ai agents":               "AI & LLMs",
    "large language model":    "AI & LLMs",
    "llm":                     "AI & LLMs",
    "generative ai":           "AI & LLMs",
    "chatgpt":                 "AI & LLMs",
    "openai":                  "AI & LLMs",
    "anthropic":               "AI & LLMs",
    "startup":                 "Startups & Funding",
    "funding round":           "Startups & Funding",
    "series a":                "Startups & Funding",
    "series b":                "Startups & Funding",
    "acquisition":             "Startups & Funding",
    "remote job":              "Jobs & Hiring",
    "tech hiring":             "Jobs & Hiring",
    "software engineer":       "Jobs & Hiring",
    "job opportunity":         "Jobs & Hiring",
    "solo travel":             "Travel & Nomad",
    "digital nomad":           "Travel & Nomad",
    "budget travel":           "Travel & Nomad",
    "travel guide":            "Travel & Nomad",
}

MAX_ARTICLES  = 40
MAX_PER_TOPIC = 4
MIN_DESCRIPTION_LENGTH = 80
ARTICLES_PER_TOPIC = 15