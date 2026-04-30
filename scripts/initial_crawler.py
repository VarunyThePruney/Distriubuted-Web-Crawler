import time
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import json

BASE_URL = "https://arxiv.org"

CATEGORIES = ["cs.AI", "cs.LG", "cs.CL", "cs.CV"]

RESULTS_PER_PAGE = 25
MAX_PAGES_PER_CATEGORY = 2  # keep small for now

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


def parse_abstract(paper_id):
    abs_url = urljoin(BASE_URL, f"/abs/{paper_id}")

    html = fetch(abs_url)
    soup = BeautifulSoup(html, "html.parser")

    def safe_extract(selector, default=""):
        return selector.text.strip() if selector else default

    title = safe_extract(soup.find("h1", class_="title")).replace("Title:", "")
    abstract = safe_extract(soup.find("blockquote", class_="abstract")).replace("Abstract:", "")

    authors_block = soup.find("div", class_="authors")
    authors = [a.text.strip() for a in authors_block.find_all("a")] if authors_block else []

    primary_subject = safe_extract(soup.find("span", class_="primary-subject"))

    submission_history = soup.find("div", class_="submission-history")
    submission_date = submission_history.text.strip() if submission_history else ""

    return {
        "paper_id": paper_id,
        "title": title,
        "authors": authors,
        "abstract": abstract,
        "primary_subject": primary_subject,
        "submission_info": submission_date,
        "url": abs_url
    }


def main():
    all_papers = []
    seen_ids = set()

    for category in CATEGORIES:
        print(f"\n=== Crawling category: {category} ===")

        paper_ids = get_paper_ids(category)

        for pid in paper_ids:
            if pid in seen_ids:
                continue

            try:
                data = parse_abstract(pid)
                all_papers.append(data)
                seen_ids.add(pid)

                print(f"Collected: {pid}")

            except Exception as e:
                print(f"Error with {pid}: {e}")

    with open("data/papers.json", "w") as f:
        json.dump(all_papers, f, indent=2)

    print(f"\nSaved {len(all_papers)} unique papers")


if __name__ == "__main__":
    main()