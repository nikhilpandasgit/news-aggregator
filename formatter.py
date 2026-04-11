from datetime import datetime

def format_digest(articles: list[dict]) -> tuple[str, str]:
    date_str = datetime.now().strftime("%B %d %Y")
    subject = f"Your news digest - {date_str}"
    
    rows_list = []
    
    for i, a in enumerate(articles, 1):
        title = a.get("title") or "Article"
        url = a.get("url") or '#'
        source = (a.get("source") or {}).get("name") or "Unknown Source"
        desc = a.get("description") or ""
        score = a.get("_score", 0)
        score_badge = f'<span style="background:#f0f0f0;color:#888;font-size:11px;padding:2px 7px;border-radius:10px;margin-left:6px;">score {score}</span>'
        
        rows_list.append(f"""
        <tr>
            <td style="padding:14px 0;border-bottom:1px solid #eee;">
                <span style="color:#888;font-size:12px">{i}. {source}</span><br>
                <a href="{url}" style="font-size:16px;font-weight:600;color:#1a1a1a;text-decoration:none;">{title}</a>{score_badge}<br>
                <p style="color:#555;font-size:14px;margin:4px 0 0;">{desc}</p>
            </td>
        </tr>
        """)
    rows = "".join(rows_list) if rows_list else "<tr><td>No articles found.</td></tr>"
    
    html_output = f"""
        <html><body style="font-family:sans-serif;max-width:600px;margin:auto;padding:24px;">
            <h2 style="color:#1a1a1a;">📰 News Digest — {date_str}</h2>
            <p style="color:#888;">{len(rows_list)} articles matched your keywords.</p>
            <table width="100%" cellpadding="0" cellspacing="0">{rows}</table>
            <p style="color:#ccc;font-size:12px;margin-top:32px;">Sent by your personal news agent.</p>
        </body></html>"""

    return subject, html_output