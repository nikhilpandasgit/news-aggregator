from datetime import datetime
from collections import defaultdict

TOPIC_COLOURS: dict[str, str] = {
    "AI & LLMs":           "#6366f1",
    "Startups & Funding":  "#0ea5e9",
    "Jobs & Hiring":       "#10b981",
    "Travel & Nomad":      "#f59e0b",
    "General":             "#6b7280",
}

DEFAULT_COLOUR = "#6b7280"

def _recency_label(recency: float) -> str:
    """Convert recency factor back to a human-friendly freshness badge."""
    if recency >= 0.95:
        return "fresh"
    if recency >= 0.75:
        return "today"
    return "older"


def _recency_badge_style(recency: float) -> str:
    if recency >= 0.95:
        return "background:#d1fae5;color:#065f46;"
    if recency >= 0.75:
        return "background:#fef3c7;color:#92400e;"
    return "background:#f3f4f6;color:#6b7280;"


def _topic_section(topic: str, articles: list[dict], start_index: int) -> str:
    colour = TOPIC_COLOURS.get(topic, DEFAULT_COLOUR)
    rows: list[str] = []

    for i, a in enumerate(articles, start_index):
        title   = a.get("title") or "Article"
        url     = a.get("url") or "#"
        source  = (a.get("source") or {}).get("name") or "Unknown Source"
        desc    = a.get("description") or ""
        score   = a.get("_score", 0)
        recency = a.get("_recency", 0.75)

        score_pct   = f"{int(score * 100)}%"
        rec_label   = _recency_label(recency)
        rec_style   = _recency_badge_style(recency)

        badge_score   = f'<span style="font-size:11px;padding:2px 8px;border-radius:10px;background:#f0f0f0;color:#888;">{score_pct}</span>'
        badge_recency = f'<span style="font-size:11px;padding:2px 8px;border-radius:10px;{rec_style}">{rec_label}</span>'

        rows.append(f"""
        <tr>
            <td style="padding:14px 0;border-bottom:1px solid #f0f0f0;">
            <span style="color:#9ca3af;font-size:12px;">{i}.&nbsp;{source}</span>
            &nbsp;{badge_score}&nbsp;{badge_recency}<br>
            <a href="{url}"
                style="font-size:15px;font-weight:600;color:#111827;text-decoration:none;line-height:1.4;">
                {title}
            </a><br>
            <p style="color:#6b7280;font-size:13px;margin:5px 0 0;line-height:1.5;">{desc}</p>
            </td>
        </tr>""")

    rows_html = "".join(rows)

    return f"""
    <tr>
        <td style="padding:20px 0 6px;">
        <span style="
            display:inline-block;
            background:{colour}18;
            color:{colour};
            font-size:11px;
            font-weight:700;
            letter-spacing:0.08em;
            text-transform:uppercase;
            padding:3px 10px;
            border-radius:20px;
            border:1px solid {colour}40;
        ">{topic}</span>
        </td>
    </tr>
    {rows_html}"""


def format_digest(articles: list[dict]) -> tuple[str, str]:
    date_str = datetime.now().strftime("%B %d, %Y")
    subject  = f"Your news digest — {date_str}"

    # group by topic
    groups: dict[str, list[dict]] = defaultdict(list)
    for a in articles:
        groups[a.get("_topic", "General")].append(a)

    # preferred topic display order
    topic_order = [
        "AI & LLMs",
        "Startups & Funding",
        "Jobs & Hiring",
        "Travel & Nomad",
        "General",
    ]

    ordered_topics = [t for t in topic_order if t in groups]
    # any unexpected topic at the end
    for t in groups:
        if t not in ordered_topics:
            ordered_topics.append(t)

    total = len(articles)
    topic_summary_parts = [
        f'<span style="color:{TOPIC_COLOURS.get(t, DEFAULT_COLOUR)};font-weight:600;">'
        f'{t} ({len(groups[t])})</span>'
        for t in ordered_topics
    ]
    topic_summary = " &middot; ".join(topic_summary_parts)

    # build all topic sections
    sections: list[str] = []
    idx = 1
    for topic in ordered_topics:
        sections.append(_topic_section(topic, groups[topic], idx))
        idx += len(groups[topic])

    all_sections = "".join(sections)

    html_output = f"""<!DOCTYPE html>
        <html>
        <body style="font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;
                    max-width:620px;margin:auto;padding:32px 24px;background:#ffffff;">

        <!-- header -->
        <table width="100%" cellpadding="0" cellspacing="0" style="margin-bottom:4px;">
            <tr>
            <td>
                <p style="margin:0;font-size:12px;color:#9ca3af;letter-spacing:0.05em;text-transform:uppercase;">
                Personal News Digest
                </p>
                <h1 style="margin:4px 0 0;font-size:22px;font-weight:700;color:#111827;">
                {date_str}
                </h1>
            </td>
            <td style="text-align:right;vertical-align:bottom;">
                <span style="font-size:28px;font-weight:700;color:#111827;">{total}</span>
                <span style="font-size:13px;color:#9ca3af;margin-left:2px;">articles</span>
            </td>
            </tr>
        </table>

        <!-- topic summary bar -->
        <p style="font-size:13px;margin:10px 0 20px;padding-bottom:16px;
                    border-bottom:2px solid #f3f4f6;color:#6b7280;">
            {topic_summary}
        </p>

        <!-- articles grouped by topic -->
        <table width="100%" cellpadding="0" cellspacing="0">
            {all_sections}
        </table>

        <!-- footer -->
        <p style="margin-top:36px;font-size:11px;color:#d1d5db;text-align:center;">
            Sent by your personal news agent &mdash; scores shown as relevance&nbsp;%
        </p>

        </body>
        </html>"""

    return subject, html_output