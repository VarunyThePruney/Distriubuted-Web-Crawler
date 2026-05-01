import time
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import re
from collections import Counter

from db import (
    get_connection,
    insert_paper,
    insert_author,
    link_paper_author,
    insert_subject,
    link_paper_subject,
    insert_keyword,
    link_paper_keyword,
    insert_stats
)


BASE_URL = "https://arxiv.org"

CATEGORIES = ["cs.AI", "cs.LG"]
RESULTS_PER_PAGE = 25
MAX_PAGES_PER_CATEGORY = 1

CRAWL_DELAY = 15  

HEADERS = {
    "User-Agent": "EducationalCrawler"
}



def fetch(url):
    print(f"Fetching: {url}")
    time.sleep(CRAWL_DELAY)

    response = requests.get(url, headers=HEADERS, timeout=30)
    response.raise_for_status()
    return response.text



def safe_text(tag):
    return tag.text.strip() if tag else ""


def extract_subjects(soup):
    subject_block = soup.find("div", class_="subheader")
    if not subject_block:
        return []

    text = subject_block.text

    if "Subjects:" in text:
        text = text.split("Subjects:")[1]

    subjects = [s.strip() for s in text.split(";")]
    return subjects


def parse_abstract(paper_id):
    abs_url = urljoin(BASE_URL, f"/abs/{paper_id}")
    html = fetch(abs_url)

    soup = BeautifulSoup(html, "html.parser")

    title = safe_text(soup.find("h1", class_="title")).replace("Title:", "")
    abstract = safe_text(soup.find("blockquote", class_="abstract")).replace("Abstract:", "")

    authors_block = soup.find("div", class_="authors")
    authors = [a.text.strip() for a in authors_block.find_all("a")] if authors_block else []

    primary_subject = safe_text(soup.find("span", class_="primary-subject"))

    submission_history = soup.find("div", class_="submission-history")
    submission_info = submission_history.text.strip() if submission_history else ""

    subjects = extract_subjects(soup)

    return {
        "paper_id": paper_id,
        "title": title,
        "authors": authors,
        "abstract": abstract,
        "primary_subject": primary_subject,
        "submission_info": submission_info,
        "subjects": subjects,
        "url": abs_url
    }



STOPWORDS = set([
    "the", "and", "is", "in", "to", "of", "for", "with",
    "on", "this", "that", "we", "by", "an", "be", "are", "as", "from"
])


def extract_keywords(text, top_n=5):
    words = re.findall(r'\b[a-zA-Z]{4,}\b', text.lower())
    words = [w for w in words if w not in STOPWORDS]

    freq = Counter(words)
    return [word for word, _ in freq.most_common(top_n)]



def compute_stats(paper):
    abstract_words = paper["abstract"].split()

    return {
        "word_count": len(abstract_words),
        "abstract_length": len(paper["abstract"]),
        "title_length": len(paper["title"]),
        "num_authors": len(paper["authors"])
    }



def get_paper_ids(category):
    paper_ids = []

    for page in range(MAX_PAGES_PER_CATEGORY):
        skip = page * RESULTS_PER_PAGE
        url = f"{BASE_URL}/list/{category}/recent?skip={skip}&show={RESULTS_PER_PAGE}"

        html = fetch(url)
        soup = BeautifulSoup(html, "html.parser")

        for dt in soup.find_all("dt"):
            link = dt.find("a", title="Abstract")
            if link:
                paper_ids.append(link.text.strip())

    return paper_ids



def main():
    conn = get_connection()
    cursor = conn.cursor()

    seen_ids = set()

    try:
        for category in CATEGORIES:
            print(f"\n=== Crawling {category} ===")

            paper_ids = get_paper_ids(category)

            for pid in paper_ids:
                if pid in seen_ids:
                    continue

                try:
                    paper = parse_abstract(pid)

                    # Insert paper
                    paper_db_id = insert_paper(cursor, paper)

                    # Authors
                    for author in paper["authors"]:
                        author_id = insert_author(cursor, author)
                        link_paper_author(cursor, paper_db_id, author_id)

                    # Subjects
                    for subj in paper["subjects"]:
                        sid = insert_subject(cursor, subj)
                        link_paper_subject(cursor, paper_db_id, sid)

                    # Keywords
                    keywords = extract_keywords(paper["abstract"])
                    for kw in keywords:
                        kid = insert_keyword(cursor, kw)
                        link_paper_keyword(cursor, paper_db_id, kid)

                    # Stats
                    stats = compute_stats(paper)
                    insert_stats(cursor, paper_db_id, stats)

                    conn.commit()

                    seen_ids.add(pid)
                    print(f"Stored: {pid}")

                except Exception as e:
                    print(f"Error processing {pid}: {e}")
                    conn.rollback()

    finally:
        cursor.close()
        conn.close()
        print("Database connection closed")


if __name__ == "__main__":
    main()