import feedparser
from datetime import datetime, timedelta, timezone

FEEDS = {
    "TechCrunch": "https://techcrunch.com/category/artificial-intelligence/feed/",
    "The Verge": "https://www.theverge.com/rss/ai-artificial-intelligence/index.xml",
    "MIT Tech Review": "https://www.technologyreview.com/topic/artificial-intelligence/feed",
    "VentureBeat": "https://venturebeat.com/category/ai/feed/",
    "Google News": "https://news.google.com/rss/search?q=artificial+intelligence&hl=en-US&gl=US&ceid=US:en",
}

HOURS_BACK = 24  # change to 168 for a weekly digest
MAX_PER_FEED = 8  # cap so one feed can't dominate
BLOCKED_PUBLISHERS = {"tradingview", "debuglies.com"}  # add more as you spot them


def fetch_articles():
    cutoff = datetime.now(timezone.utc) - timedelta(hours=HOURS_BACK)
    articles, seen_titles = [], set()

    for source, url in FEEDS.items():
        feed = feedparser.parse(url)
        count = 0

        for entry in feed.entries:
            if count >= MAX_PER_FEED:
                break

            published = entry.get("published_parsed") or entry.get("updated_parsed")
            if not published:
                continue
            published_dt = datetime(*published[:6], tzinfo=timezone.utc)
            if published_dt < cutoff:
                continue

            title = entry.get("title", "").strip()
            publisher = source

            # Google News titles look like "Headline - Publisher"
            if source == "Google News" and " - " in title:
                title, publisher = title.rsplit(" - ", 1)
                publisher = publisher.strip()
                if any(blocked in publisher.lower() for blocked in BLOCKED_PUBLISHERS):
                    continue

            if title.lower() in seen_titles:
                continue
            seen_titles.add(title.lower())

            articles.append(
                {
                    "source": publisher,
                    "title": title,
                    "link": entry.get("link", ""),
                    "published": published_dt,
                }
            )
            count += 1

    articles.sort(key=lambda a: a["published"], reverse=True)
    return articles


if __name__ == "__main__":
    articles = fetch_articles()
    print(f"Found {len(articles)} AI articles from the last {HOURS_BACK} hours\n")
    for a in articles:
        print(f"[{a['source']}] {a['title']}")
        print(f"   {a['link']}\n")
