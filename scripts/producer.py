import requests
from bs4 import BeautifulSoup
import redis

# Redis connection
r = redis.Redis(host="localhost", port=6379, db=0)

BASE_URL = "https://arxiv.org/list/cs/new"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; DistributedCrawler/1.0)"
}

# Strong vs weak keywords
STRONG_AI_KEYWORDS = [
    "llm", "large language model", "transformer",
    "deep learning", "neural network"
]

WEAK_AI_KEYWORDS = [
    "machine learning", "ai", "artificial intelligence",
    "nlp", "computer vision", "reinforcement learning"
]


def compute_priority(title):
    """
    Returns priority between 0 and 100
    Lower = higher priority
    """
    title_lower = title.lower()

    score = 50  # base score (mid priority)

    # Strong matches → big boost
    for kw in STRONG_AI_KEYWORDS:
        if kw in title_lower:
            score -= 20

    # Weak matches → smaller boost
    for kw in WEAK_AI_KEYWORDS:
        if kw in title_lower:
            score -= 10

    # Clamp between 0 and 100
    score = max(0, min(score, 100))

    return score


def get_papers():
    print("Fetching paper list...")

    try:
        response = requests.get(BASE_URL, headers=HEADERS, timeout=10)
        response.raise_for_status()
    except requests.RequestException as e:
        print("Error:", e)
        return []

    soup = BeautifulSoup(response.text, "html.parser")

    papers = []

    dl = soup.find("dl")
    if not dl:
        return papers

    for dt in dl.find_all("dt"):
        link = dt.find("a", title="Abstract")
        if not link:
            continue

        paper_id = link.text.strip()

        dd = dt.find_next_sibling("dd")
        title_tag = dd.find("div", class_="list-title")

        title = ""
        if title_tag:
            title = title_tag.text.replace("Title:", "").strip()

        papers.append((paper_id, title))

    return papers


def main():
    print("Starting producer...")

    papers = get_papers()

    for pid, title in papers:

        if not r.sismember("seen_ids", pid):

            priority = compute_priority(title)

            r.zadd("paper_queue", {pid: priority})
            r.sadd("seen_ids", pid)

            print(f"Queued: {pid} | priority={priority} | {title}")

    print("Done.")


if __name__ == "__main__":
    main()