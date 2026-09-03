#!/usr/bin/env python3
"""
Local test — bypasses IMAP entirely, uses sample_newsletter.html instead,
so you can verify parse_articles() and the RSS output before wiring up
real email credentials.

Run:
    pip install beautifulsoup4 feedgen
    python scripts/test_local.py
"""

import os
from generate_feed import parse_articles, build_feed

SAMPLE_PATH = os.path.join(os.path.dirname(__file__), "sample_newsletter.html")
OUTPUT_PATH = os.path.join(os.path.dirname(__file__), "..", "docs", "feed.xml")


def main():
    with open(SAMPLE_PATH, "r", encoding="utf-8") as f:
        html = f.read()

    articles = parse_articles(html)
    print(f"Parsed {len(articles)} articles:\n")
    for a in articles:
        print(f"- {a['title']}")
        print(f"  {a['summary']}\n")

    fg = build_feed(articles, "Sample Newsletter — Test Edition")
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    fg.rss_file(OUTPUT_PATH)
    print(f"Wrote feed to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
