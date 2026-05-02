import requests
import time
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import re
from collections import Counter

BASE_URL = "https://arxiv.org"

HEADERS = {
    "User-Agent": "DistributedCrawler/1.0 (educational project)"
}



def acquire_rate_limit(r, key="rate_limit", delay=3):
    """
    Ensures only ONE request every 'delay' seconds across ALL workers
    """
    while True:
        now = time.time()

        last = r.get(key)

        if last is None:
            r.set(key, now)
            return

        elapsed = now - float(last)

        if elapsed >= delay:
            r.set(key, now)
            return

        time.sleep(delay - elapsed)



def fetch(url, r):
    acquire_rate_limit(r, delay=3)  #GLOBAL control

    print(f"Fetching: {url}")

    res = requests.get(url, headers=HEADERS, timeout=30)
    res.raise_for_status()
    return res.text



def safe_text(tag):
    return tag.text.strip() if tag else ""


def extract_subjects(soup):
    block = soup.find("div", class_="subheader")
    if not block:
        return []

    text = block.text
    if "Subjects:" in text:
        text = text.split("Subjects:")[1]

    return [s.strip() for s in text.split(";")]


def parse_abstract(pid, r):
    url = urljoin(BASE_URL, f"/abs/{pid}")
    html = fetch(url, r)

    soup = BeautifulSoup(html, "html.parser")

    title = safe_text(soup.find("h1", class_="title")).replace("Title:", "")
    abstract = safe_text(soup.find("blockquote", class_="abstract")).replace("Abstract:", "")

    authors_block = soup.find("div", class_="authors")
    authors = [a.text.strip() for a in authors_block.find_all("a")] if authors_block else []

    primary_subject = safe_text(soup.find("span", class_="primary-subject"))

    submission = safe_text(soup.find("div", class_="submission-history"))

    subjects = extract_subjects(soup)

    return {
        "paper_id": pid,
        "title": title,
        "authors": authors,
        "abstract": abstract,
        "primary_subject": primary_subject,
        "submission_info": submission,
        "subjects": subjects,
        "url": url
    }



STOPWORDS = set([
    "the", "and", "is", "in", "to", "of", "for", "with",
    "on", "this", "that", "we", "by", "an", "be", "are", "as", "from"
])


def extract_keywords(text, top_n=5):
    words = re.findall(r'\b[a-zA-Z]{4,}\b', text.lower())
    words = [w for w in words if w not in STOPWORDS]

    freq = Counter(words)
    return [w for w, _ in freq.most_common(top_n)]



def compute_stats(paper):
    words = paper["abstract"].split()

    return {
        "word_count": len(words),
        "abstract_length": len(paper["abstract"]),
        "title_length": len(paper["title"]),
        "num_authors": len(paper["authors"])
    }