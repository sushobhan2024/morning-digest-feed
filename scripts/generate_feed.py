import os
import email
import imaplib
from email.header import decode_header
from email.utils import format_datetime
from datetime import datetime, timezone
from bs4 import BeautifulSoup
from feedgen.feed import FeedGenerator

IMAP_HOST = os.environ.get("IMAP_HOST", "imap.gmail.com")
IMAP_PORT = int(os.environ.get("IMAP_PORT", "993"))
SENDER_FILTER = os.environ.get("SENDER_FILTER", "")
MAILBOX = os.environ.get("MAILBOX", "INBOX")
FEED_TITLE = os.environ.get("FEED_TITLE", "Morning Digest News")

OUTPUT_PATH = os.path.join(os.path.dirname(__file__), "..", "docs", "feed.xml")


def fetch_latest_html():
    """Connect via IMAP and return the HTML body + subject of the most recent matching email."""
    imap_user = os.environ["IMAP_USER"]
    imap_pass = os.environ["IMAP_PASS"]

    conn = imaplib.IMAP4_SSL(IMAP_HOST, IMAP_PORT, timeout=30)
    conn.login(imap_user, imap_pass)
    conn.select(MAILBOX)

    search_criteria = f'(FROM "{SENDER_FILTER}")' if SENDER_FILTER else "ALL"
    status, data = conn.search(None, search_criteria)
    if status != "OK" or not data[0]:
        raise RuntimeError("No matching emails found.")

    latest_id = data[0].split()[-1]
    status, msg_data = conn.fetch(latest_id, "(RFC822)")
    raw_email = msg_data[0][1]
    msg = email.message_from_bytes(raw_email)

    html_body = None
    if msg.is_multipart():
        for part in msg.walk():
            if part.get_content_type() == "text/html":
                html_body = part.get_payload(decode=True).decode(
                    part.get_content_charset() or "utf-8", errors="replace"
                )
                break
    else:
        html_body = msg.get_payload(decode=True).decode(
            msg.get_content_charset() or "utf-8", errors="replace"
        )

    conn.logout()

    subject = decode_header(msg.get("Subject", ""))[0][0]
    if isinstance(subject, bytes):
        subject = subject.decode(errors="replace")

    return html_body, subject


def parse_articles(html):
    """
    Turn the newsletter HTML into a flat list of articles:
    [{title, summary, link}, ...]
    """
    soup = BeautifulSoup(html, "html.parser")
    articles = []

    for article_div in soup.find_all("div", class_="article"):
        headline_div = article_div.find("div", class_="headline")
        if not headline_div:
            continue
        title = headline_div.get_text(strip=True)
        if not title:
            continue

        subhead_div = article_div.find("div", class_="subhead")
        summary = subhead_div.get_text(strip=True) if subhead_div else ""

        link_tag = headline_div.find_parent("a")
        link = os.environ.get("FEED_SITE_URL", "")
        if link_tag and link_tag.get("originalsrc"):
            link = link_tag["originalsrc"]
        elif link_tag and link_tag.get("href"):
            link = link_tag["href"]

        articles.append({"title": title, "summary": summary, "link": link})

    return articles


def build_feed(articles, feed_subject):
    feed_site_url = os.environ["FEED_SITE_URL"]
    fg = FeedGenerator()
    fg.title(FEED_TITLE)
    fg.link(href=feed_site_url, rel="alternate")
    fg.description(feed_subject or "Personal newsletter feed")
    fg.language("en")

    now = datetime.now(timezone.utc)

    for a in articles:
        fe = fg.add_entry()
        fe.title(a["title"])
        fe.description(a["summary"])
        fe.link(href=a["link"])
        fe.pubDate(format_datetime(now))

    return fg


def main():
    html, subject = fetch_latest_html()
    articles = parse_articles(html)

    if not articles:
        raise RuntimeError("No articles parsed — check parse_articles() against your real newsletter HTML.")

    fg = build_feed(articles, subject)

    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    fg.rss_file(OUTPUT_PATH)

    print(f"Wrote {len(articles)} articles to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()