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
        "series A",
        "series B",
        "seed funding",
        "venture capital",
        "raises funding",
        "completes fundraising",
    ],
    "Jobs & Hiring": [
        "remote job",
        "tech hiring",
        "job opportunity",
    ],
    "Travel & Nomad": [
        "solo travel",
        "digital nomad",
        "budget travel",
        "travel guide",
    ],
}

TITLE_SCOPED_TERMS: set[str] = {"AI", "LLM", "generative AI"}


KEYWORDS: list = [
    # AI
    "AI",
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
    "seed funding",
    "venture capital",
    "raises funding",
    "completes fundraising",

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
    "ai": "AI & LLMs",
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
    "seed funding":            "Startups & Funding",
    "venture capital":         "Startups & Funding",
    "raises $":                "Startups & Funding",    
    "remote job":              "Jobs & Hiring",
    "tech hiring":             "Jobs & Hiring",
    "software engineer":       "Jobs & Hiring",
    "job opportunity":         "Jobs & Hiring",
    "solo travel":             "Travel & Nomad",
    "digital nomad":           "Travel & Nomad",
    "budget travel":           "Travel & Nomad",
    "travel guide":            "Travel & Nomad",
}

BLOCKED_DOMAINS: set[str] = {
    "pypi.org",
    "npmjs.com",
}

BLOCKED_SOURCE_NAMES: set[str] = {"Internet", "Unknown"}

MAX_ARTICLES  = 40
MAX_PER_TOPIC = 6
MIN_DESCRIPTION_LENGTH = 80
ARTICLES_PER_TOPIC = 25
TITLE_SIMILARITY_THRESHOLD = 0.6
MIN_SCORE_THRESHOLD=0.35

GROQ_MODEL="llama-3.3-70b-versatile"
SUMMARISE_TOP_K=6
