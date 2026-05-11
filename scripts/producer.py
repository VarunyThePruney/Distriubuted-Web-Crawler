import requests
from bs4 import BeautifulSoup
import redis
from pybloom_live import BloomFilter

from scripts.worker import process

r = redis.Redis(host="localhost", port=6379, db=0)

HEADERS = {
    "User-Agent": "DistributedCrawler/1.0"
}

STRONG_AI_KEYWORDS = [
    "llm",
    "large language model",
    "transformer",
    "deep learning",
    "neural network"
]

WEAK_AI_KEYWORDS = [
    "machine learning",
    "ai",
    "artificial intelligence",
    "nlp",
    "computer vision",
    "reinforcement learning"
]

bloom = BloomFilter(capacity=500000, error_rate=0.001)


def compute_priority(title):
    title = title.lower()
    score = 50

    for kw in STRONG_AI_KEYWORDS:
        if kw in title:
            score -= 20

    for kw in WEAK_AI_KEYWORDS:
        if kw in title:
            score -= 10

    return max(0, min(score, 100))


def fetch_page(skip):
    url = f"https://arxiv.org/list/cs/pastweek?skip={skip}&show=100"
    response = requests.get(url, headers=HEADERS, timeout=10)
    soup = BeautifulSoup(response.text, "html.parser")
    
    papers = []

    dl = soup.find("dl")
    if not dl:
        return papers

    for dt in dl.find_all("dt"):
        link = dt.find("a", title="Abstract")
        if not link:
            continue

        pid = link.text.strip()

        dd = dt.find_next_sibling("dd")
        title_tag = dd.find("div", class_="list-title")

        title = ""

        if title_tag:
            title = title_tag.text.replace("Title:", "").strip()
        papers.append((pid, title))

    return papers


def get_current_skip():
    value = r.get("current_skip")
    if value is None:
        return 0
    return int(value.decode())


def save_next_skip(skip):
    next_skip = skip + 100
    if next_skip > 2000:
        next_skip = 0
    r.set("current_skip", next_skip)


def main():
    skip = get_current_skip()
    print(f"Fetching skip={skip}")
    papers = fetch_page(skip)
    added = 0
    skipped = 0
    
    for pid, title in papers:
        if pid in bloom:
            skipped += 1
            continue
        priority = compute_priority(title)
        process.delay(pid)
        bloom.add(pid)
        added += 1
        print(f"Queued: {pid} | priority={priority}")

    save_next_skip(skip)

    print("\nDone.")
    print(f"Added: {added}")
    print(f"Skipped: {skipped}")


if __name__ == "__main__":
    main()