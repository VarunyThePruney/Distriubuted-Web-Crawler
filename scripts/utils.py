import requests
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; DistributedCrawler/1.0)"
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


def compute_priority(title):
    title_lower = title.lower()
    score = 50
    for kw in STRONG_AI_KEYWORDS:
        if kw in title_lower:
            score -= 20

    for kw in WEAK_AI_KEYWORDS:
        if kw in title_lower:
            score -= 10
            
    score = max(0, min(score, 100))
    return score


def parse_abstract(pid, r=None):
    url = f"https://arxiv.org/abs/{pid}"

    try:
        response = requests.get(
            url,
            headers=HEADERS,
            timeout=10
        )
        response.raise_for_status()

    except requests.RequestException as e:
        print(f"Request Error: {e}")
        return None

    soup = BeautifulSoup(response.text, "html.parser")

    title = ""

    title_tag = soup.find("h1", class_="title")

    if title_tag:
        title = (title_tag.text.replace("Title:", "").strip())
        
    abstract = ""

    abstract_tag = soup.find("blockquote",class_="abstract")

    if abstract_tag:
        abstract = (abstract_tag.text.replace("Abstract:", "").strip())

    authors = []

    author_div = soup.find("div", class_="authors")

    if author_div:

        author_links = author_div.find_all("a")

        for a in author_links:
            authors.append(a.text.strip())

    subjects = []

    subject_span = soup.find("span", class_="primary-subject")

    if subject_span:
        subjects.append(
            subject_span.text.strip()
        )

    published = "Unknown"

    history_div = soup.find("div", class_="submission-history")

    if history_div:
        lines = history_div.text.split("\n")

        for line in lines:
            line = line.strip()

            if "[" in line and "]" in line:
                published = line
                break

    priority_score = compute_priority(title)

    return {
        "paper_id": pid,
        "title": title,
        "abstract": abstract,
        "authors": authors,
        "subjects": subjects,
        "published": published,
        "priority_score": priority_score
    }


def extract_keywords(text):
    words = text.lower().split()

    keywords = []

    for word in words:
        if len(word) > 6:
            keywords.append(word)
    return list(set(keywords))[:10]


def compute_stats(paper):
    abstract = paper["abstract"]
    return {
        "word_count": len(abstract.split()),
        "keyword_count": len(extract_keywords(abstract))
    }