import time
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import json

crawl_delay = 15

base_url = "https://arxiv.org"
catagory_url = "https://arxiv.org/list/cs.AI/recent"

HEADER = {"User-Agent": "InitialCrawlerProject"}

def fetch(url):
    time.sleep(crawl_delay)
    response = requests.get(url, headers=HEADER, timeout=15)
    response.raise_for_status()
    return response.text

def get_paperids():
    html = fetch(catagory_url)
    soup = BeautifulSoup(html, "html.parser")
    
    paper_ids = []
    for dt in soup.find_all("dt"):
        link = dt.find("a", title="Abstract")
        if link:
            paper_ids.append(link.text.strip())
            
    return paper_ids

def parse_pid(paper_id):
    abs_url = urljoin(base_url, f"/abs/{paper_id}")
    html = fetch(abs_url)
    soup = BeautifulSoup(html, "html.parser")
    
    title = soup.find("h1", class_="title").text.replace("Title", "").strip()
    abstract = soup.find("blockquote", class_="abstract").text.replace("Abstract", "").strip()
    authors = [a.text.strip() for a in soup.find("div", class_="authors").find_all("a")]
    subjects = soup.find("span", class_="primary-subject").text.strip()
    
    return {
        "paper_id": paper_id,
        "title": title,
        "authors": authors,
        "abstract": abstract,
        "subjects": subjects,
        "abs_url": abs_url
    }
    
def main():
    papers = []
    paper_ids = get_paperids()
    
    for pid in paper_ids[:5]:
        print(f"crawling {pid}")
        
        data = parse_pid(pid)
        papers.append(data)
        
        with open("data/papers.json", "w") as f:
            json.dump(papers, f, indent=2)
        

if __name__ == "__main__":
    main()